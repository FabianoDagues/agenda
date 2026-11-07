"""Teste ponta a ponta (somente SQLite local temporario, sem banco Railway)."""
import re

from fastapi.testclient import TestClient


def csrf_from(html):
    match = re.search(r'name="token" value="([^"]+)"', html)
    assert match, html[:250]
    return match.group(1)


def test_full_agenda_flow(tmp_path, monkeypatch):
    monkeypatch.delenv('RAILWAY_ENVIRONMENT', raising=False)
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///' + str(tmp_path / 'agenda_teste.db'))
    monkeypatch.setenv('SECRET_KEY', 'teste-apenas-local-que-nao-esta-em-producao')
    monkeypatch.setenv('COOKIE_SECURE', '0')
    monkeypatch.setenv('ADMIN_EMAIL', 'user1@example.com')
    monkeypatch.setenv('ADMIN_NAME', 'Pessoa 1')
    monkeypatch.setenv('ADMIN_PASSWORD', 'SenhaTeste-usuario1-12')
    monkeypatch.setenv('PARTNER_EMAIL', 'user2@example.com')
    monkeypatch.setenv('PARTNER_NAME', 'Pessoa 2')
    monkeypatch.setenv('PARTNER_PASSWORD', 'SenhaTeste-usuario2-12')
    from app.main import app, SessionLocal, User, Event

    with TestClient(app, follow_redirects=True) as client:
        health = client.get('/health')
        assert health.status_code == 200
        assert health.json() == {'status': 'ok', 'version': '2.1.0', 'database': 'sqlite'}
        assert client.get('/').url.path == '/login'
        first = client.get('/login')
        assert first.status_code == 200
        assert 'Nossa Agenda' in first.text
        token = csrf_from(first.text)
        rejected = client.post('/login', data={'email':'user1@example.com','password':'errada','token':token})
        assert rejected.status_code == 401
        assert 'E-mail ou senha inválidos.' in rejected.text
        good = client.post('/login', data={'email':'user1@example.com','password':'SenhaTeste-usuario1-12','token':token})
        assert good.status_code == 200
        assert good.url.path == '/'
        assert 'Pessoa 1' in good.text and 'Pessoa 2' in good.text
        token = csrf_from(good.text)
        with SessionLocal() as db:
            members = db.query(User).order_by(User.id).all()
            assert len(members) == 2
            second_id = members[1].id
        created = client.post('/events', data={'title':'Consulta médica', 'description':'Trazer documentos', 'start':'2026-11-12T15:00', 'end':'2026-11-12T16:00','owner_id':str(second_id), 'category':'Saúde', 'location':'Clínica', 'remind_minutes':'30','token':token})
        assert created.status_code == 200
        assert created.url.path == '/'
        with SessionLocal() as db:
            events = db.query(Event).all()
            assert len(events) == 1
            eid = events[0].id
            assert events[0].completed is False
            assert events[0].title == 'Consulta médica'
        edited = client.post(f'/events/{eid}/edit',data={'title':'Retorno médico','start':'2026-11-12T15:30','owner_id':str(second_id),'category':'Saúde','remind_minutes':'60','token':token})
        assert edited.status_code == 200
        with SessionLocal() as db: assert db.get(Event,eid).title == 'Retorno médico'
        completed = client.post(f'/events/{eid}/toggle',data={'token':token})
        assert completed.status_code == 200
        with SessionLocal() as db:
            assert db.get(Event,eid).completed is True
        assert '"completed": true' in completed.text
        assert client.post('/theme',data={'color':'green','token':token}).status_code==200
        assert 'data-theme="green"' in client.get('/').text
        uncompleted = client.post(f'/events/{eid}/toggle',data={'token':token})
        assert uncompleted.status_code == 200
        deleted = client.post(f'/events/{eid}/delete',data={'token':token})
        assert deleted.status_code==200
        with SessionLocal() as db: assert db.query(Event).count() == 0
        for asset in ('/static/app.js','/static/style.css','/static/icon-192.png','/static/icon-512.png','/static/icon-180.png','/manifest.webmanifest','/service-worker.js','/favicon.ico'):
            assert client.get(asset).status_code == 200, asset
        assert 'icon-192.png' in client.get('/manifest.webmanifest').text
        assert client.post('/logout',data={'token':token}).url.path=='/login'

    # Segunda conta: login individual em outro cliente, com mesmo banco.
    with TestClient(app) as partner:
        first = partner.get('/login')
        response = partner.post('/login',data={'email':'user2@example.com','password':'SenhaTeste-usuario2-12','token':csrf_from(first.text)},follow_redirects=True)
        assert response.status_code == 200 and 'Pessoa 2' in response.text
