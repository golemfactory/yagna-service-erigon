from datetime import datetime

from service_manager import ServiceWrapper


class ErigonServiceWrapper(ServiceWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = None
        self._created_at = datetime.utcnow()
        self._stopped_at = None

    def stop(self):
        super().stop()
        if self._stopped_at is None:
            self._stopped_at = datetime.utcnow()

    def api_repr(self):
        data = {
            'id': self.id,
            'status': self.status,
            'name': self.name,
            'init_params': self.start_args[0],
            'created_at': self._created_at.isoformat(),
        }
        if self.status == 'running':
            data['url'] = self.service.url
            data['auth'] = self.service.auth
            data['network'] = self.service.network
        elif self.stopped:
            data['stopped_at'] = self._stopped_at.isoformat()

        return data
