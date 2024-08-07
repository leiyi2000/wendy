import aiodocker
import structlog
from fastapi import APIRouter
from fastapi.responses import Response

from wendy import models, agent
from wendy.cluster import Cluster


router = APIRouter()
log = structlog.get_logger()


@router.get(
    "/download/{id}",
    description="下载存档",
)
async def download(id: int):
    deploy = await models.Deploy.get(id=id)
    cluster = Cluster.model_validate(deploy.content)
    async with aiodocker.Docker(cluster.docker_api) as docker:
        tar_file = await agent.download_archive(cluster.id, docker)
    tar_file.fileobj.seek(0)
    return Response(
        content=tar_file.fileobj.read(),
        headers={"Content-Disposition": f"attachment; filename=archive_{id}.tar"},
    )
