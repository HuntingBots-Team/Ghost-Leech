from asyncio import (
sleep,
gather
)

from tghbot import (
LOGGER,
intervals,
nzb_jobs,
nzb_listener_lock,
sabnzbd_client,
task_dict_lock,
)
from tghbot.helper.ext_utils.bot_utils import new_task
from tghbot.helper.ext_utils.status_utils import (
get_task_by_gid,
speed_string_to_bytes
)
from tghbot.helper.ext_utils.task_manager import (
limit_checker,
stop_duplicate_check
)

async def _remove_job(nzo_id, mid):
    (
        res1,
        _
    ) = await gather(
        sabnzbd_client.delete_history(
            nzo_id,
            delete_files=True
        ),
        sabnzbd_client.delete_category(f"{mid}"),
    )
    if not res1:
        await sabnzbd_client.delete_job(
            nzo_id,
            True
        )
    async with nzb_listener_lock:
        if nzo_id in nzb_jobs:
            del nzb_jobs[nzo_id]


@new_task
async def _on_download_error(err, nzo_id, button=None):
    task = await get_task_by_gid(nzo_id)
    await task.update() # type: ignore
    LOGGER.info(f"Cancelling Download: {task.name()}") # type: ignore
    await gather(
        task.listener.on_download_error( # type: ignore
            err,
            button
        ),
        _remove_job(
            nzo_id,
            task.listener.mid # type: ignore
        ),
        sabnzbd_client.delete_job(
            nzo_id,
            delete_files=True
        ),
        sabnzbd_client.delete_category(f"{task.listener.mid}"), # type: ignore
    )
    async with nzb_listener_lock:
        if nzo_id in nzb_jobs:
            del nzb_jobs[nzo_id]


@new_task
async def _change_status(nzo_id, status):
    task = await get_task_by_gid(nzo_id)
    async with task_dict_lock:
        task.cstatus = status # type: ignore


@new_task
async def _stop_duplicate(nzo_id):
    task = await get_task_by_gid(nzo_id)
    await task.update() # type: ignore
    task.listener.name = task.name() # type: ignore
    (
        msg,
        button
    ) = await stop_duplicate_check(task.listener) # type: ignore
    if msg:
        _on_download_error(
            msg,
            nzo_id,
            button
        ) # type: ignore


@new_task
async def _size_checker(nzo_id):
    task = await get_task_by_gid(nzo_id)
    await task.update() # type: ignore
    task.listener.size = speed_string_to_bytes(task.size()) # type: ignore
    limit_exceeded = await limit_checker(
        task.listener, # type: ignore
        is_nzb=True
    )
    if limit_exceeded:
        LOGGER.info(
            f"NZB Limit Exceeded: {task.name()} | {task.size()}" # type: ignore
        )
        _on_download_error(
            limit_exceeded,
            nzo_id
        ) # type: ignore


@new_task
async def _on_download_complete(nzo_id):
    task = await get_task_by_gid(nzo_id)
    await task.listener.on_download_complete() # type: ignore
    if intervals["stopAll"]:
        return
    await _remove_job(
        nzo_id,
        task.listener.mid # type: ignore
    )


@new_task
async def _nzb_listener():
    while not intervals["stopAll"]:
        async with nzb_listener_lock:
            try:
                jobs = (await sabnzbd_client.get_history())["history"]["slots"]
                downloads = (await sabnzbd_client.get_downloads())["queue"]["slots"]
                if len(nzb_jobs) == 0:
                    intervals["nzb"] = ""
                    break
                for job in jobs:
                    nzo_id = job["nzo_id"]
                    if nzo_id not in nzb_jobs:
                        continue
                    if job["status"] == "Completed":
                        if not nzb_jobs[nzo_id]["uploaded"]:
                            nzb_jobs[nzo_id]["uploaded"] = True
                            await _on_download_complete(nzo_id) # type: ignore
                            nzb_jobs[nzo_id]["status"] = "Completed"
                    elif job["status"] == "Failed":
                        await _on_download_error(
                            job["fail_message"],
                            nzo_id
                        ) # type: ignore
                    elif job["status"] in [
                        "QuickCheck",
                        "Verifying",
                        "Repairing",
                        "Fetching",
                        "Moving",
                        "Extracting",
                    ]:
                        if job["status"] != nzb_jobs[nzo_id]["status"]:
                            await _change_status(
                                nzo_id,
                                job["status"]
                            ) # type: ignore
                for dl in downloads:
                    nzo_id = dl["nzo_id"]
                    if nzo_id not in nzb_jobs:
                        continue
                    if (
                        dl["status"] == "Downloading"
                        and not nzb_jobs[nzo_id]["stop_dup_check"]
                        and not dl["filename"].startswith("Trying")
                    ):
                        nzb_jobs[nzo_id]["stop_dup_check"] = True
                        await _stop_duplicate(nzo_id) # type: ignore
                        await _size_checker(nzo_id) # type: ignore
            except Exception as e:
                LOGGER.error(str(e))
        await sleep(3)


async def on_download_start(nzo_id):
    async with nzb_listener_lock:
        nzb_jobs[nzo_id] = {
            "uploaded": False,
            "stop_dup_check": False,
            "status": "Downloading",
        }
        if not intervals["nzb"]:
            intervals["nzb"] = await _nzb_listener()
