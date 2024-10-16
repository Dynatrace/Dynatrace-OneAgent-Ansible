from abc import abstractmethod

from util.test_data_types import DeploymentResult


class DeploymentRunner:
    @abstractmethod
    def run_deployment(self) -> DeploymentResult:
        raise NotImplementedError

