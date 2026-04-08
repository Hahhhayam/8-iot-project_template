from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

INITIAL_GRAVITY_BASELINE = 16500
current_gravity_baseline = INITIAL_GRAVITY_BASELINE
BUMP_THRESHOLD = 1000
POTHOLE_THRESHOLD = 4000


def _classify_road_state(z_axis_value: float) -> str:
    global current_gravity_baseline

    current_z = abs(z_axis_value)
    deviation = abs(current_z - current_gravity_baseline)
    current_gravity_baseline = current_z

    if deviation >= POTHOLE_THRESHOLD:
        return "pothole"
    if deviation >= BUMP_THRESHOLD:
        return "bump"
    return "normal"


def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    road_state = _classify_road_state(agent_data.accelerometer.z)
    return ProcessedAgentData(road_state=road_state, agent_data=agent_data)
