import copy
import json
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.mother import MotherJourney
from app.api import mother as api
from app.db.mother_seed_importer import validate_content, import_content

CONTENT = json.loads((Path(__file__).resolve().parents[1] / 'seed/mothers-6-12-preview-v1.json').read_text())

def answers(weight):
    return {s['id']: next(o['id'] for o in s['options'] if o['weight'] == weight) for s in CONTENT['situations']}

class ScoringTests(unittest.TestCase):
    def test_profiles(self):
        high = api.score(CONTENT, answers(2))
        self.assertTrue(high['all_strong'])
        self.assertEqual(len(high['strengths']), 4)
        low = api.score(CONTENT, answers(0))
        self.assertEqual(low['strengths'], [])
        self.assertEqual(len(low['recommended']), 4)
        for values in ({s['id']: None for s in CONTENT['situations']}, {'s01': 'a'}):
            result = api.score(CONTENT, values)
            self.assertEqual(result['recommended'], [])
            self.assertTrue(all(a['band'] == 'insufficient' for a in result['areas']))
        self.assertTrue(all(a['band'] == 'mixed' for a in api.score(CONTENT, answers(1))['areas']))
        self.assertNotIn('weight', json.dumps(high))

    def test_validator(self):
        validate_content(CONTENT)
        for mutate in [lambda c: c['situations'].pop(), lambda c: c['practices'].pop(), lambda c: c.update(preview=False), lambda c: c['review_anchors'].append('s01'), lambda c: c['situations'][0]['options'][0].update(weight=3)]:
            invalid = copy.deepcopy(CONTENT); mutate(invalid)
            with self.assertRaises(ValueError): validate_content(invalid)

class PersistenceTests(unittest.TestCase):
    def setUp(self):
        if engine.url.host not in ('localhost', '127.0.0.1'): self.skipTest('Local database only')
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.db = Session(bind=self.connection, join_transaction_mode='create_savepoint')
        self.clock = patch.object(api, 'now', return_value=datetime(2026, 9, 16, 18, tzinfo=timezone.utc))
        self.now = self.clock.start()
        started = api.start(api.Start(timezone='Europe/Berlin'), self.db)
        self.id, self.token = started['id'], started['owner_token']

    def tearDown(self):
        if hasattr(self,'connection'):
            self.clock.stop(); self.db.close(); self.transaction.rollback(); self.connection.close()

    def test_flow(self):
        draft = api.AssessmentInput(answers={'s01':'a'})
        api.assessment(self.id,'baseline',draft,self.db,self.token)
        self.assertEqual(api.resume(self.id,self.db,self.token)['answers'],{'s01':'a'})
        self.assertNotEqual(self.db.get(MotherJourney,self.id).owner_token_hash,self.token)
        for attempt in [lambda: api.resume(self.id,self.db,'wrong'), lambda: api.assessment(self.id,'baseline',draft,self.db,'wrong'), lambda: api.focus(self.id,api.FocusInput(focus_code='example'),self.db,'wrong'), lambda: api.checkin(self.id,1,api.CheckinInput(outcome='easy'),self.db,'wrong'), lambda: api.delete(self.id,self.db,'wrong')]:
            with self.assertRaises(HTTPException) as ctx: attempt()
            self.assertEqual(ctx.exception.status_code,404)
        submitted=api.AssessmentInput(answers=answers(1),submit=True)
        for _ in range(2): api.assessment(self.id,'baseline',submitted,self.db,self.token)
        api.focus(self.id,api.FocusInput(focus_code='example'),self.db,self.token)
        with self.assertRaises(HTTPException): api.checkin(self.id,2,api.CheckinInput(outcome='easy'),self.db,self.token)
        result=api.checkin(self.id,1,api.CheckinInput(outcome='difficult',repeat_requested=True),self.db,self.token)
        self.assertEqual(result['current_day'],1)
        for _ in range(2):
            result=api.checkin(self.id,1,api.CheckinInput(outcome='difficult'),self.db,self.token)
            self.assertEqual(result['current_day'],2); self.assertIsNone(result['practice'])
        with self.assertRaises(HTTPException): api.checkin(self.id,2,api.CheckinInput(outcome='easy'),self.db,self.token)
        self.now.return_value += timedelta(days=8)
        self.assertEqual(api.resume(self.id,self.db,self.token)['practice']['day'],2)
        result=api.checkin(self.id,2,api.CheckinInput(outcome='not_yet'),self.db,self.token)
        self.assertEqual(result['current_day'],2)
        api.checkin(self.id,2,api.CheckinInput(outcome='no_opportunity'),self.db,self.token)
        self.now.return_value += timedelta(days=1)
        result=api.checkin(self.id,3,api.CheckinInput(outcome='easy'),self.db,self.token)
        self.assertEqual(result['status'],'preview_complete'); self.assertIsNone(result['practice'])
        self.assertNotIn('weight',json.dumps(result))
        api.delete(self.id,self.db,self.token)
        with self.assertRaises(HTTPException): api.resume(self.id,self.db,self.token)

    def test_import_pinning(self):
        old=self.db.get(MotherJourney,self.id).content_release_id
        self.assertEqual(import_content(self.db,CONTENT,True).id,old)
        changed=copy.deepcopy(CONTENT); changed['practices'][0]['title']['en']='Changed'
        with self.assertRaises(ValueError): import_content(self.db,changed,True)
        changed['version']='test-next-preview'
        self.assertNotEqual(import_content(self.db,changed,True).id,old)
        self.assertEqual(api.resume(self.id,self.db,self.token)['content']['version'],CONTENT['version'])

class PreviewAccessTests(unittest.TestCase):
    def test_signed_sessions_and_passwords(self):
        from app.core import preview_access as gate
        from app.core.config import settings
        with patch.object(settings,'PREVIEW_SESSION_SECRET','a'*40), patch.object(settings,'PREVIEW_PASSWORD_HASH',gate.password_hash('synthetic-test-pass')):
            self.assertTrue(gate.password_valid('synthetic-test-pass'))
            self.assertFalse(gate.password_valid('wrong'))
            token=gate.session_token()
            self.assertTrue(gate.session_valid(token))
            self.assertFalse(gate.session_valid(token+'x'))
            with patch.object(gate.time,'time',return_value=gate.time.time()+gate.TTL+1):
                self.assertFalse(gate.session_valid(token))
