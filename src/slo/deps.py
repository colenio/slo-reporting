from slo.service import SloService

SLO_SERVICE = SloService()

def get_slo_service() -> SloService:
    return SLO_SERVICE