import json
from typing import Dict, Tuple, List

from job_generator.manifests import minio_secret_ref
from job_generator.manifests.abstract_manifest_creator import AbstractManifestCreator, YamlManifest, JobName
from job_generator.yaml_data import YamlData
from job_generator.yaml_job_generator import JobManifestGenerator


class ProjectDownloadManifestCreator(AbstractManifestCreator):

    DOCKER_IMAGE = "watermodelling/project-download-job:latest"
    CONTAINER_NAME = "project-download"

    ENV = [
        minio_secret_ref.endpoint,
        minio_secret_ref.access_key,
        minio_secret_ref.secret_key
    ]

    def __init__(self, project_name: str, hydrus_models: List[str], modflow_model: str):
        super().__init__(project_name=project_name,
                         docker_image=ProjectDownloadManifestCreator.DOCKER_IMAGE,
                         container_name=ProjectDownloadManifestCreator.CONTAINER_NAME)
        self.hydrus_models = hydrus_models
        self.modflow_model = modflow_model

    def _get_job_prefix(self) -> str:
        return f"download-{self.project_name}"

    def create_manifest(self) -> Tuple[YamlManifest, JobName]:
        yaml_data = YamlData(job_prefix=self._get_job_prefix(),
                             docker_image=self.docker_image,
                             container_name=self.container_name,
                             description=f"Download job for project {self.project_name}")
        yaml_data.set_env(ProjectDownloadManifestCreator.ENV)
        return JobManifestGenerator.prepare_kubernetes_job(yaml_data), yaml_data.job_name

    def get_redis_command(self) -> str:
        args = ["download_project.sh", self.project_name, f"modflow:{self.modflow_model}"]

        for model in self.hydrus_models:
            args.append(f"hydrus:{model}")

        cmd = {
            "executable": "bash",
            "args": args,
            "inputs": [],
            "outputs": []
        }
        return json.dumps(cmd)
