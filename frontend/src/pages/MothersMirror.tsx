import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useLanguage } from '../i18n/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';
import AboutCreatorModal from '../components/AboutCreatorModal';
import ConfirmationModal from '../components/ConfirmationModal';

type Copy = { en: string; ar: string };
type Area = { code: string; title: Copy; descriptions: Record<string, Copy> };
type Situation = { id: string; area: string; text: Copy; options: { id: string; text: Copy }[] };
type Practice = { day: number; area: string; title: Copy; value: Copy; action: Copy; words: Copy; smaller: Copy };
type Outcome = 'easy' | 'difficult' | 'not_yet' | 'no_opportunity';
type State = {
  id: string; status: string; current_day: number; focus_code: string | null; timezone: string;
  next_available_at: string | null; answers: Record<string, string | null>;
  content: { version: string; areas: Area[]; situations: Situation[]; practices: Practice[] };
  result: null | { areas: { code: string; band: string; evidence: { situation_id: string; option_id: string }[] }[];
    recommended: string[]; strengths: string[]; all_strong: boolean };
  practice: Practice | null; checkins: { day: number; outcome: Outcome; repeat_requested: boolean }[];
};
type Locator = { id: string; token: string };
const KEY = 'miraati_mother_journey';
const PENDING = 'miraati_mother_pending';
const root = '/mothers-mirror/journeys';

export default function MothersMirror() {
  const { language } = useLanguage();
  const txt = (en: string, ar: string) => language === 'ar' ? ar : en;
  const copy = (value: Copy) => value[language];
  const [state, setState] = useState<State | null>(null);
  const [locator, setLocator] = useState<Locator | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState(false);
  const [storageError, setStorageError] = useState(false);
  const [index, setIndex] = useState(0);
  const [focus, setFocus] = useState('');
  const [outcome, setOutcome] = useState<Outcome | ''>('');
  const [repeat, setRepeat] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const headers = (owner: Locator) => ({ 'X-Mother-Owner-Token': owner.token });

  function accept(next: State) {
    setState(next);
    setFocus(next.focus_code || (next.result?.recommended.length === 1 ? next.result.recommended[0] : ''));
    const checkin = next.checkins.find(c => c.day === next.current_day);
    setOutcome(checkin?.outcome || '');
    setRepeat(checkin?.repeat_requested || false);
  }
  async function load(owner: Locator) {
    let next: State = (await api.get(`${root}/${owner.id}`, { headers: headers(owner) })).data;
    const pending = localStorage.getItem(PENDING);
    if (pending && next.status === 'baseline') {
      const change = JSON.parse(pending);
      if (change.id === owner.id) {
        // Draft answers stay local, just like the quick and long questionnaires.
        next = { ...next, answers: change.payload.answers };
      }
    }
    accept(next);
    const missing = next.content.situations.findIndex(s => !(s.id in next.answers));
    setIndex(missing === -1 ? next.content.situations.length - 1 : missing);
  }
  useEffect(() => {
    async function init() {
      try {
        const saved = localStorage.getItem(KEY);
        if (saved) {
          const owner = JSON.parse(saved);
          setLocator(owner);
          await load(owner);
        }
      } catch { setError(true); }
      finally { setBusy(false); }
    }
    void init();
    // The locator is read once; changing language must not restart a journey.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function run(action: () => Promise<void>) {
    setBusy(true); setError(false);
    try { await action(); } catch { setError(true); } finally { setBusy(false); }
  }
  async function start() {
    await run(async () => {
      // Check persistence before creating a journey whose capability could be lost.
      try { localStorage.setItem('mother_storage_check', '1'); localStorage.removeItem('mother_storage_check'); }
      catch { setStorageError(true); return; }
      const response = await api.post(root, { age_band: '6-12', timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC' });
      const owner = { id: response.data.id, token: response.data.owner_token };
      setLocator(owner);
      localStorage.setItem(KEY, JSON.stringify(owner));
      accept(response.data); setIndex(0);
    });
  }
  function saveAnswer(value: string | null) {
    if (!state || !locator) return;
    const answers = { ...state.answers, [state.content.situations[index].id]: value };
    try {
      localStorage.setItem(PENDING, JSON.stringify({ id: locator.id, payload: { answers, submit: false } }));
      setState({ ...state, answers });
      setStorageError(false);
    } catch { setStorageError(true); }
  }
  async function submitAssessment() {
    if (!state || !locator) return;
    await run(async () => {
      const response = await api.put(`${root}/${locator.id}/assessments/baseline`,
        { answers: state.answers, submit: true }, { headers: headers(locator) });
      accept(response.data);
      localStorage.removeItem(PENDING);
    });
  }
  async function put(path: string, payload: unknown) {
    if (!locator) return;
    await run(async () => accept((await api.put(`${root}/${locator.id}/${path}`, payload, { headers: headers(locator) })).data));
  }
  const card = 'rounded-soft border border-accent/80 bg-white/70 p-6 shadow-soft-card backdrop-blur-sm';
  const choice = (selected: boolean) => `w-full rounded-soft border px-5 py-4 text-start text-sm font-medium leading-relaxed text-ink shadow-soft-card backdrop-blur-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:text-base ${selected ? 'border-accent/80 bg-white shadow-soft-float' : 'border-sand/80 bg-white/60 hover:border-accent/60 hover:bg-white/75'}`;
  const q = state?.content.situations[index];
  const result = state?.result;
  const areaTitle = (code: string) => copy(state!.content.areas.find(a => a.code === code)!.title);
  const outcomes: [Outcome, string, string][] = [['easy', 'Tried it easily', 'جرّبتها بسهولة'], ['difficult', 'Tried it with difficulty', 'جرّبتها بصعوبة'], ['not_yet', 'Not tried yet', 'لم أجرّبها بعد'], ['no_opportunity', 'No opportunity', 'لم تتح الفرصة']];

  return <main className="relative min-h-screen overflow-hidden bg-cream text-ink" dir={language === 'ar' ? 'rtl' : 'ltr'}>
    <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(197,168,128,0.18)_0%,_rgba(246,241,234,0)_60%)]" />
    <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_rgba(58,80,107,0.08)_0%,_rgba(246,241,234,0)_70%)]" />
    <div className="pointer-events-none absolute inset-0 opacity-[0.35] [background-image:radial-gradient(rgba(58,80,107,0.06)_1px,transparent_1px)] [background-size:28px_28px]" />
    <div className="absolute left-4 top-4 z-20 sm:left-8 sm:top-6">
      <AboutCreatorModal placement="header" />
    </div>
    <div className="absolute top-4 right-4 z-20 sm:right-8 sm:top-6">
      <LanguageSwitcher className="border border-sand/70 shadow-soft-card backdrop-blur-sm" />
    </div>
    <div className="relative z-10 mx-auto w-full max-w-5xl px-4 pb-16 pt-24 sm:px-6 sm:pt-24 md:pt-28 lg:px-8 lg:pt-32">
      <nav className="mb-8"><Link to="/" className="text-primary underline">{txt('Miraati home', 'الرئيسية — مرآتي')}</Link></nav>
      <p className="mb-3 text-sm text-primary">{txt('Three-practice preview · Draft content', 'معاينة بثلاث ممارسات · محتوى مسودة')}</p>
      <h1 className="mb-4 text-3xl font-semibold">{txt("Mother’s Miraat", 'مرآة الأم')}</h1>
      <p className="mb-6 text-sm leading-relaxed text-muted">{txt('For mothers of children aged 6–12. These reflections describe your answers, not a diagnosis or a parenting grade. Draft content has not been expert reviewed or scientifically validated.', 'لأمهات الأطفال من ٦ إلى ١٢ سنة. تصف هذه المرآة إجاباتكِ، وليست تشخيصًا أو تقييمًا لأمومتكِ. المحتوى مسودة لم يخضع لمراجعة خبراء أو تحقق علمي.')}</p>
      {error && <div role="alert" className={`${card} mb-5`}><p>{txt('We could not confirm the save or load. Your journey has not been reset. Retry before continuing.', 'تعذر تأكيد الحفظ أو التحميل. لم نعد ضبط رحلتكِ. أعيدي المحاولة قبل المتابعة.')}</p><button disabled={busy} className="pill-button mt-3" onClick={() => locator ? void run(() => load(locator)) : void run(async () => { setError(false); })}>{txt('Retry saved journey', 'إعادة محاولة تحميل الرحلة')}</button></div>}
      {storageError && <p role="alert">{txt('Enable browser storage to save and resume this preview.', 'فعّلي تخزين المتصفح لحفظ هذه المعاينة ومتابعتها.')}</p>}
      <p role="status" className="mb-4 min-h-[1.5rem] text-sm text-muted">{busy ? txt('Saving / loading…', 'جارٍ الحفظ / التحميل…') : ''}</p>
      <fieldset disabled={busy || error} className="min-w-0 space-y-6 disabled:opacity-70">
      {!state && !locator && <section className={card}>
        <h2 className="text-xl font-semibold">{txt('A moment to notice your responses', 'لحظة لفهم استجابتكِ')}</h2>
        <p className="my-4 leading-relaxed">{txt('Keep one child aged 6–12 in mind. Think about what usually happened over the past seven days, not the ideal answer. No name or account is needed.', 'فكري في طفل واحد عمره من ٦ إلى ١٢ سنة. فكّري فيما حدث غالبًا خلال الأيام السبعة الماضية، لا في الإجابة المثالية. لا نحتاج اسمًا أو حسابًا.')}</p>
        <button className="pill-button pill-button-primary" onClick={start}>{txt('Start my mirror', 'ابدئي مرآتكِ')}</button>
      </section>}
      {state?.status === 'baseline' && q && <section className={card}>
        <div className="mb-6">
          <div className="mb-3 flex justify-between text-sm text-muted">
            <span>{txt('Situation', 'الموقف')}</span><span>{index + 1} / {state.content.situations.length}</span>
          </div>
          <div role="progressbar" aria-label={txt('Situation progress', 'التقدم في المواقف')} aria-valuenow={index + 1} aria-valuemin={0} aria-valuemax={state.content.situations.length} className="h-2 w-full overflow-hidden rounded-full bg-sand/60">
            <div className="h-2 rounded-full bg-primary transition-all" style={{ width: `${((index + 1) / state.content.situations.length) * 100}%` }} />
          </div>
        </div>
        <p className="mb-4 text-sm text-muted">{txt('Think about the past seven days with the same child.', 'فكري في الأيام السبعة الماضية مع الطفل نفسه.')}</p>
        <h2 className="mb-6 text-center text-2xl font-semibold leading-relaxed text-ink">{copy(q.text)}</h2>
        <div className="space-y-3">{q.options.map(o => <button key={o.id} className={choice(state.answers[q.id] === o.id)} aria-pressed={state.answers[q.id] === o.id} onClick={() => saveAnswer(o.id)}>{copy(o.text)}</button>)}
          <button className={choice(q.id in state.answers && state.answers[q.id] === null)} aria-pressed={q.id in state.answers && state.answers[q.id] === null} onClick={() => saveAnswer(null)}>{txt('I did not encounter a similar situation', 'لم أمرّ بموقف مشابه')}</button>
        </div>
        <div className="mt-6 flex flex-wrap justify-between gap-3"><button className="pill-button pill-button-secondary" disabled={index === 0} onClick={() => setIndex(index - 1)}>{txt('Back', 'السابق')}</button>
          {index < state.content.situations.length - 1 ? <button className="pill-button pill-button-primary" disabled={!(q.id in state.answers)} onClick={() => setIndex(index + 1)}>{txt('Next', 'التالي')}</button> : <button className="pill-button pill-button-primary" disabled={Object.keys(state.answers).length !== state.content.situations.length} onClick={submitAssessment}>{txt('See my mirror', 'شاهدي مرآتكِ')}</button>}
        </div>
        <p className="mt-3 min-h-[2.5rem] text-sm text-muted" aria-live="polite">{q.id in state.answers ? txt('Saved in this browser. You can change it before submitting.', 'تم الحفظ في هذا المتصفح. يمكنكِ تغيير الإجابة قبل الإرسال.') : ''}</p>
      </section>}
      {state?.status === 'focus' && result && <>
        <section className={card}><h2 className="mb-3 text-2xl font-semibold">{txt('Your mirror now', 'مرآتكِ الآن')}</h2>
          <p className="leading-relaxed">{result.all_strong ? txt('Your answered areas show supportive responses. Choose something to keep practicing; we are not identifying a weakness.', 'أظهرت المجالات التي أجبتِ عنها استجابات داعمة. اختاري ما تودين مواصلة التدرب عليه دون افتراض نقطة ضعف.') : result.recommended.length ? txt('According to your answers, the areas below offer a place to practice. Examples explain the suggestion; circumstances differ from week to week.', 'بحسب إجاباتكِ، تقدم المجالات أدناه فرصة للممارسة. توضح الأمثلة سبب الاقتراح، وقد تختلف الظروف من أسبوع لآخر.') : txt('There are not enough answered situations to describe an area. You can still choose a focus for practice.', 'لا توجد مواقف مجابة كافية لوصف مجال. يمكنكِ مع ذلك اختيار مجال للممارسة.')}</p>
          <h3 className="mt-5 font-semibold">{result.strengths.length ? txt('A strength in your answers', 'قوة ظهرت في إجاباتكِ') : txt('What we noticed', 'ما لاحظناه')}</h3>
          <p className="mt-2">{result.strengths.length ? areaTitle(result.strengths[0]) : txt('Your answers do not give enough support to name a strength. That is a limit of this mirror, not a verdict on you.', 'لا تقدم إجاباتكِ دعمًا كافيًا لتسمية قوة. هذا حد لهذه المرآة وليس حكمًا عليكِ.')}</p>
          {result.strengths.length > 0 && <p className="mt-2">{copy(state.content.areas.find(a => a.code === result.strengths[0])!.descriptions.strong)}</p>}
          {!result.all_strong && result.recommended.length > 0 && <><h3 className="mt-5 font-semibold">{txt('A place to practice', 'مساحة للممارسة')}</h3><p className="mt-2">{result.recommended.map(areaTitle).join(language === 'ar' ? '، ' : ', ')}</p><p className="mt-2 text-sm">{txt('These areas had the least support among your sufficiently answered situations. See your selected responses below.', 'كانت هذه المجالات الأقل دعمًا بين المواقف التي أجبتِ عنها بما يكفي. اطلعي على استجاباتكِ المختارة أدناه.')}</p></>}
        </section>
        <div className="grid gap-4 sm:grid-cols-2">{result.areas.map(a => {
          const area = state.content.areas.find(item => item.code === a.code)!;
          return <section className={card} key={a.code}><h3 className="font-semibold">{copy(area.title)}</h3><p className="my-3">{a.band === 'insufficient' ? txt('We need more situations to describe this area.', 'نحتاج مواقف أكثر لوصف هذا المجال.') : copy(area.descriptions[a.band])}</p>
            {a.evidence.slice(0, 1).map(e => { const s = state.content.situations.find(s => s.id === e.situation_id)!; return <div key={e.situation_id} className="text-sm text-muted"><p>{copy(s.text)}</p><p className="mt-2">{txt('You selected: ', 'اخترتِ: ')}{copy(s.options.find(o => o.id === e.option_id)!.text)}</p></div>; })}
          </section>;
        })}</div>
        <section className={card}><h2 className="text-xl font-semibold">{txt('What would you like to practice?', 'ما الذي تريدين التدرب عليه؟')}</h2>
          <p className="my-3 text-sm text-muted">{!result.recommended.length || result.all_strong ? txt('Choose the area you would like to keep practicing.', 'اختاري المجال الذي تودين مواصلة ممارسته.') : result.recommended.length > 1 ? txt('Several areas are tied; choose the one that matters to you.', 'تساوت عدة مجالات؛ اختاري الأقرب لاحتياجكِ.') : txt('The suggestion uses the lowest sufficiently answered area. You can choose another.', 'يعتمد الاقتراح على المجال الأقل دعمًا بإجابات كافية. يمكنكِ اختيار غيره.')}</p>
          <div className="space-y-3">{state.content.areas.map(a => <button key={a.code} className={choice(focus === a.code)} aria-pressed={focus === a.code} onClick={() => setFocus(a.code)}>{copy(a.title)}{result.recommended.includes(a.code) && !result.all_strong ? txt(' · Suggested', ' · مقترح') : ''}</button>)}</div>
          <p className="my-4">{txt('This preview has three shared practices with your focus kept visible. It is not a personalized 30-day program. One new practice opens per local calendar day; missed days preserve your pending card.', 'تتضمن المعاينة ثلاث ممارسات مشتركة مع إبقاء اختياركِ ظاهرًا، وليست برنامجًا مخصصًا لثلاثين يومًا. تتاح ممارسة جديدة كل يوم حسب توقيتكِ المحلي، وتبقى الممارسة المعلقة عند الغياب.')}</p>
          <button disabled={!focus} className="pill-button pill-button-primary" onClick={() => put('focus', { focus_code: focus })}>{txt('Begin practice', 'ابدئي الممارسة')}</button>
        </section>
      </>}
      {state?.focus_code && <p className="rounded-2xl bg-white/70 p-4">{txt('My focus: ', 'مجال ممارستي: ')}{areaTitle(state.focus_code)}</p>}
      {state?.status === 'practice' && !state.practice && <section className={card}>
        <h2 className="text-xl font-semibold">{txt('Your check-in is saved', 'تم حفظ متابعتكِ')}</h2><p className="my-4">{txt('Your next practice opens on ', 'تتاح ممارستكِ التالية في ')}{state.next_available_at && new Date(state.next_available_at).toLocaleString(language, { timeZone: state.timezone })} ({state.timezone}). {txt('Return when you can. There is no streak to lose.', 'عودي حين تستطيعين. لا توجد سلسلة أيام تخسرينها.')}</p>
        <button className="pill-button" onClick={() => locator && run(() => load(locator))}>{txt('Check availability', 'تحقق من الإتاحة')}</button>
      </section>}
      {state?.practice && <section className={card}>
        <p className="mb-2 text-sm text-primary">{txt(`Practice ${state.current_day} of 3`, `الممارسة ${state.current_day} من 3`)} · {copy(state.practice.value)}</p>
        <h2 className="text-2xl font-semibold">{copy(state.practice.title)}</h2>
        {state.practice.area === state.focus_code && <p className="mt-2 text-sm text-primary">{txt('Related to your chosen focus', 'مرتبطة بما اخترتِ التدرب عليه')}</p>}
        <p className="my-5 text-lg leading-relaxed">{copy(state.practice.action)}</p>
        <blockquote className="rounded-2xl bg-cream p-4">{copy(state.practice.words)}</blockquote>
        <h3 className="mb-3 mt-6 font-semibold">{txt('How did it go?', 'كيف كانت التجربة؟')}</h3>
        <div className="grid gap-3 sm:grid-cols-2">{outcomes.map(([code,en,ar]) => <button key={code} className={choice(outcome === code)} aria-pressed={outcome === code} onClick={() => { setOutcome(code); setRepeat(false); }}>{txt(en,ar)}</button>)}</div>
        {outcome === 'difficult' && <div className="my-4 rounded-2xl bg-cream p-4"><h3 className="font-semibold">{txt('A smaller version', 'نسخة أصغر')}</h3><p className="my-2">{copy(state.practice.smaller)}</p><label className="flex gap-3"><input type="checkbox" checked={repeat} onChange={e => setRepeat(e.target.checked)} />{txt('Keep this practice to try again', 'احتفظي بهذه الممارسة للمحاولة مجددًا')}</label></div>}
        {outcome === 'no_opportunity' && <p className="mt-4">{txt('No opportunity is not failure. Continue when the next card opens.', 'عدم توفر الفرصة ليس إخفاقًا. تابعي حين تتاح البطاقة التالية.')}</p>}
        <button disabled={!outcome} className="pill-button pill-button-primary mt-5" onClick={() => put(`checkins/${state.current_day}`, { outcome, repeat_requested: repeat })}>{txt('Save check-in', 'احفظي المتابعة')}</button>
        {state.checkins.some(c => c.day === state.current_day) && <p role="status" className="mt-3">{txt('Saved. This practice stays here until you are ready to continue.', 'تم الحفظ. تبقى الممارسة هنا حتى تستعدي للمتابعة.')}</p>}
      </section>}
      {state?.status === 'preview_complete' && <section className={card}><h2 className="text-2xl font-semibold">{txt('You reached the end of this preview', 'وصلتِ إلى نهاية هذه المعاينة')}</h2><p className="my-4">{txt('All three practice check-ins are saved. The remaining practices and later review are not available yet. Check-ins record participation, not proof of improvement or changes in your child.', 'تم حفظ متابعة الممارسات الثلاث. بقية الممارسات والمراجعة اللاحقة غير متاحة بعد. تسجل المتابعات المشاركة ولا تثبت تحسنًا أو تغيرًا لدى طفلكِ.')}</p></section>}
      {state && state.checkins.length > 0 && <details className={card}><summary>{txt('Saved check-ins', 'المتابعات المحفوظة')}</summary><ul className="mt-3 space-y-2">{state.checkins.map(c => <li key={c.day}>{txt(`Practice ${c.day}`, `الممارسة ${c.day}`)}: {txt(outcomes.find(o => o[0] === c.outcome)![1], outcomes.find(o => o[0] === c.outcome)![2])}</li>)}</ul></details>}
      </fieldset>
      <p className="mt-8 text-sm leading-relaxed text-muted">{txt('Save and resume works in this browser. Clearing browser storage loses automatic access. There is no cross-device recovery in this preview.', 'يمكنكِ الحفظ والمتابعة في هذا المتصفح. مسح بيانات المتصفح يفقد الوصول التلقائي. لا تتوفر استعادة عبر الأجهزة في هذه المعاينة.')}</p>
      {state && <div className="mt-5 text-sm"><button disabled={busy} className="underline" onClick={() => setConfirmDelete(true)}>{txt('Delete my journey', 'احذفي رحلتي')}</button></div>}
      <ConfirmationModal
        isOpen={confirmDelete}
        title={txt('Delete my journey?', 'حذف رحلتي؟')}
        message={txt('This permanently removes this journey and its answers and check-ins.', 'سيحذف هذا الرحلة وإجاباتها ومتابعاتها نهائيًا.')}
        confirmLabel={txt('Confirm deletion', 'تأكيد الحذف')}
        cancelLabel={txt('Keep my journey', 'احتفظي برحلتي')}
        onCancel={() => setConfirmDelete(false)}
        onConfirm={() => {
          if (busy || !locator) return;
          setConfirmDelete(false);
          void run(async () => {
            await api.delete(`${root}/${locator.id}`, { headers: headers(locator) });
            localStorage.removeItem(KEY);
            localStorage.removeItem(PENDING);
            setState(null);
            setLocator(null);
          });
        }}
      />
      {state && <p className="mt-4 text-xs text-muted">{state.content.version}</p>}
    </div>
  </main>;
}
