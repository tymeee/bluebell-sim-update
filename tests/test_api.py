from fastapi.testclient import TestClient
import simulator_api


def test_api_readiness_validation_auth_and_result(monkeypatch):
    monkeypatch.setattr(simulator_api,'API_KEY','test-key')
    with TestClient(simulator_api.app) as client:
        assert client.get('/health').json()['status']=='ready'
        payload={'model':'index','age':84,'years_until_retirement':0,'simulations':100,'seed':9}
        assert client.post('/api/simulate',json=payload).status_code==401
        headers={'X-API-Key':'test-key'}
        result=client.post('/api/simulate',json=payload,headers=headers)
        assert result.status_code==200, result.text
        assert result.json()['server_seconds']>=result.json()['simulation_seconds']
        assert len(result.json()['ending_values'])==100
        assert client.post('/api/simulate',json={**payload,'simulations':1001},headers=headers).status_code==422
        class Full:
            def acquire(self,blocking): return False
        monkeypatch.setattr(simulator_api,'slots',Full())
        busy=client.post('/api/simulate',json=payload,headers=headers)
        assert busy.status_code==429
        assert busy.headers['retry-after']=='2'
