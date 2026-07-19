import React, { useEffect, useMemo, useState } from 'react';
import QRCode from 'qrcode';
import { useLanguage } from '../../i18n/LanguageContext';
import { journeyApi } from '../../services/api';
import { SharedJourneyResult } from '../../types';
import logo from '../../assets/logo.png';
import { generateResultImage } from '../../sharing/resultImage';

type Props = {
  report: SharedJourneyResult;
  owner?: { testRunId: number; ownerToken: string };
  existingLink?: string;
};

const ResultSharingActions: React.FC<Props> = ({ report, owner, existingLink }) => {
  const { t, language } = useLanguage();
  const copy = t.journey.sharing;
  const [link, setLink] = useState(existingLink ?? '');
  const [expiresAt, setExpiresAt] = useState('');
  const [showConsent, setShowConsent] = useState(false);
  const [showQr, setShowQr] = useState(false);
  const [qrDataUrl, setQrDataUrl] = useState('');
  const [status, setStatus] = useState('');
  const [busy, setBusy] = useState(false);
  const imageFilename = `${language === 'ar' ? 'مرآتي' : 'miraati'}-result-${language}.png`;

  const imageLabels = useMemo(
    () => ({
      title: copy.imageTitle,
      quick: t.journey.typeLabels.quick,
      deep: t.journey.typeLabels.deep,
      completed: copy.completed,
      genes: copy.sections.genes,
      archetypes: copy.sections.archetypes,
      quranValues: copy.sections.quranValues,
      prophetTraits: copy.sections.prophetTraits,
      activation: copy.sections.activation,
      createdWith: copy.createdWith,
    }),
    [copy, t]
  );

  useEffect(() => {
    if (!showQr || !link) return;
    QRCode.toDataURL(link, { width: 320, margin: 2, errorCorrectionLevel: 'M' })
      .then(setQrDataUrl)
      .catch(() => setStatus(copy.error));
  }, [showQr, link, copy.error]);

  const getImage = () => generateResultImage(report, imageLabels, logo, language);
  const downloadBlob = (blob: Blob) => {
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = imageFilename;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const downloadImage = async () => {
    setBusy(true);
    setStatus('');
    try {
      downloadBlob(await getImage());
      setStatus(copy.downloaded);
    } catch {
      setStatus(copy.error);
    } finally {
      setBusy(false);
    }
  };

  const shareImage = async () => {
    setBusy(true);
    setStatus('');
    try {
      const blob = await getImage();
      const file = new File([blob], imageFilename, { type: 'image/png' });
      if (navigator.share && (!navigator.canShare || navigator.canShare({ files: [file] }))) {
        try {
          await navigator.share({ files: [file], title: copy.imageTitle, text: copy.shareText });
          return;
        } catch (error) {
          if ((error as DOMException).name === 'AbortError') return;
        }
      }
      downloadBlob(blob);
      setStatus(copy.shareFallback);
    } catch {
      setStatus(copy.error);
    } finally {
      setBusy(false);
    }
  };

  const createLink = async () => {
    if (!owner) return;
    setBusy(true);
    setStatus('');
    try {
      const result = await journeyApi.createResultShare(owner.testRunId, language, owner.ownerToken);
      setLink(`${window.location.origin}/share#${result.token}`);
      setExpiresAt(result.expires_at);
      setShowConsent(false);
      setStatus(copy.linkCreated);
    } catch {
      setStatus(copy.error);
    } finally {
      setBusy(false);
    }
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(link);
      setStatus(copy.copied);
    } catch {
      setStatus(copy.copyFallback);
    }
  };

  const shareLink = async () => {
    if (navigator.share) {
      try {
        await navigator.share({ title: copy.imageTitle, text: copy.shareText, url: link });
        return;
      } catch (error) {
        if ((error as DOMException).name === 'AbortError') return;
      }
    }
    await copyLink();
  };

  return (
    <section className="mt-6 rounded-soft border border-sand/80 bg-white/60 p-5 text-start">
      <h3 className="text-xl font-semibold text-ink">{copy.title}</h3>
      <p className="mt-1 text-sm text-muted">{copy.subtitle}</p>
      <div className="mt-4 flex flex-wrap gap-3">
        <button type="button" className="btn-secondary" disabled={busy} onClick={() => void downloadImage()}>
          {copy.downloadImage}
        </button>
        <button type="button" className="btn-secondary" disabled={busy} onClick={() => void shareImage()}>
          {copy.shareImage}
        </button>
        {owner && !link && (
          <>
            <button type="button" className="btn-secondary" disabled={busy} onClick={() => setShowConsent(true)}>
              {copy.createLink}
            </button>
            <button
              type="button"
              className="btn-secondary"
              disabled={busy}
              onClick={() => {
                setShowQr(true);
                setShowConsent(true);
              }}
            >
              {copy.showQr}
            </button>
          </>
        )}
        {link && (
          <>
            <button type="button" className="btn-secondary" onClick={() => void copyLink()}>{copy.copyLink}</button>
            <button type="button" className="btn-secondary" onClick={() => void shareLink()}>{copy.shareLink}</button>
            <button type="button" className="btn-secondary" onClick={() => setShowQr((value) => !value)}>{copy.showQr}</button>
          </>
        )}
      </div>

      {showConsent && (
        <div className="mt-4 rounded-lg border border-accent/60 bg-cream p-4">
          <p className="text-sm text-ink">{copy.consent}</p>
          <p className="mt-2 text-xs text-muted">{copy.privacy}</p>
          <div className="mt-3 flex gap-2">
            <button type="button" className="btn-primary" disabled={busy} onClick={() => void createLink()}>{copy.confirmCreate}</button>
            <button type="button" className="btn-secondary" onClick={() => setShowConsent(false)}>{copy.cancel}</button>
          </div>
        </div>
      )}

      {link && (
        <div className="mt-4 space-y-2">
          <label className="block text-sm font-medium text-ink" htmlFor="private-result-link">{copy.privateLink}</label>
          <input id="private-result-link" className="w-full rounded-lg border border-sand bg-white px-3 py-2 text-sm" readOnly value={link} onFocus={(event) => event.currentTarget.select()} />
          {expiresAt && <p className="text-xs text-muted">{copy.expires} {new Intl.DateTimeFormat(language, { dateStyle: 'medium' }).format(new Date(expiresAt))}</p>}
        </div>
      )}
      {showQr && qrDataUrl && (
        <div className="mt-4 flex justify-center rounded-lg bg-white p-4">
          <img src={qrDataUrl} alt={copy.qrAlt} className="h-64 w-64" />
        </div>
      )}
      {status && <p role="status" className="mt-3 text-sm text-primary">{status}</p>}
    </section>
  );
};

export default ResultSharingActions;
