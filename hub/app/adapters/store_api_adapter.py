import json
import logging
from typing import List

import pydantic_core
import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url.rstrip("/")

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        """
        Save the processed road data to the Store API.
        Parameters:
            processed_agent_data_batch (dict): Processed road data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        if not processed_agent_data_batch:
            logging.info("Skipping store save because the batch is empty")
            return True

        if isinstance(processed_agent_data_batch, ProcessedAgentData):
            processed_agent_data_batch = [processed_agent_data_batch]

        try:
            payload = [
                processed_agent_data.model_dump(mode="json")
                for processed_agent_data in processed_agent_data_batch
            ]
            response = requests.post(
                f"{self.api_base_url}/processed_agent_data/", json=payload
            )
            if response.ok:
                return True

            logging.error(
                "Failed to save processed agent data. Status: %s, Response: %s",
                response.status_code,
                response.text,
            )
            return False
        except (requests.RequestException, pydantic_core.PydanticSerializationError) as exc:
            logging.exception("Error while saving processed agent data: %s", exc)
            return False
