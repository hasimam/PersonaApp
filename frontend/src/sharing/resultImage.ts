import { SharedJourneyResult } from '../types';
import { Language } from '../i18n/translations';

export type ResultImageLabels = {
  title: string;
  quick: string;
  deep: string;
  completed: string;
  genes: string;
  archetypes: string;
  quranValues: string;
  prophetTraits: string;
  activation: string;
  createdWith: string;
};

const loadImage = (src: string): Promise<HTMLImageElement> =>
  new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = reject;
    image.src = src;
  });

export async function generateResultImage(
  report: SharedJourneyResult,
  labels: ResultImageLabels,
  logoUrl: string,
  language: Language
): Promise<Blob> {
  await document.fonts?.ready;
  const canvas = document.createElement('canvas');
  canvas.width = 1080;
  canvas.height = 1920;
  const context = canvas.getContext('2d');
  if (!context) {
    throw new Error('Canvas is unavailable');
  }

  const rtl = language === 'ar';
  const edge = 86;
  const boxInset = 34;
  const textX = rtl ? canvas.width - edge - boxInset : edge + boxInset;
  const valueX = rtl ? edge + boxInset : canvas.width - edge - boxInset;
  context.fillStyle = '#F6F1EA';
  context.fillRect(0, 0, canvas.width, canvas.height);
  const gradient = context.createRadialGradient(540, 160, 20, 540, 400, 800);
  gradient.addColorStop(0, 'rgba(197,168,128,0.22)');
  gradient.addColorStop(1, 'rgba(246,241,234,0)');
  context.fillStyle = gradient;
  context.fillRect(0, 0, canvas.width, 900);
  context.textAlign = rtl ? 'right' : 'left';
  context.direction = rtl ? 'rtl' : 'ltr';
  context.fillStyle = '#24364A';

  const drawCenteredLine = (text: string, y: number) => {
    if (!rtl || !text.includes('PersonaApp')) {
      context.textAlign = 'center';
      context.direction = rtl ? 'rtl' : 'ltr';
      context.fillText(text, canvas.width / 2, y);
      return;
    }

    const arabic = text.replace('PersonaApp', '').trim();
    const latin = 'PersonaApp';
    const gap = 14;
    const arabicWidth = context.measureText(arabic).width;
    const latinWidth = context.measureText(latin).width;
    const startX = (canvas.width - arabicWidth - latinWidth - gap) / 2;

    context.direction = 'ltr';
    context.textAlign = 'left';
    context.fillText(latin, startX, y);
    context.direction = 'rtl';
    context.textAlign = 'right';
    context.fillText(arabic, startX + latinWidth + gap + arabicWidth, y);
  };

  try {
    const logo = await loadImage(logoUrl);
    const ratio = Math.min(250 / logo.width, 180 / logo.height);
    const width = logo.width * ratio;
    const height = logo.height * ratio;
    context.drawImage(logo, (canvas.width - width) / 2, 55, width, height);
  } catch {
    // Branding footer remains if the logo cannot be loaded.
  }

  context.textAlign = 'center';
  context.font = '700 52px Tajawal, Segoe UI, sans-serif';
  drawCenteredLine(labels.title, 280);
  context.textAlign = 'center';
  context.direction = rtl ? 'rtl' : 'ltr';
  context.font = '400 27px Tajawal, Segoe UI, sans-serif';
  context.fillStyle = '#667085';
  const journeyLabel = report.journey_type === 'deep' ? labels.deep : labels.quick;
  const completed = new Intl.DateTimeFormat(language, { dateStyle: 'medium' }).format(
    new Date(report.completed_at)
  );
  context.fillText(`${journeyLabel}  •  ${labels.completed} ${completed}`, 540, 330);

  let y = 400;
  const section = (title: string, rows: Array<{ name: string; value: string }>) => {
    if (!rows.length) return;
    const boxHeight = 84 + rows.length * 58;
    context.fillStyle = 'rgba(255,255,255,0.76)';
    context.strokeStyle = 'rgba(197,168,128,0.75)';
    context.lineWidth = 2;
    context.beginPath();
    context.roundRect(edge, y, canvas.width - edge * 2, boxHeight, 24);
    context.fill();
    context.stroke();

    context.textAlign = rtl ? 'right' : 'left';
    context.fillStyle = '#24364A';
    context.font = '700 31px Tajawal, Segoe UI, sans-serif';
    context.fillText(title, textX, y + 54);
    rows.forEach((row, index) => {
      const rowY = y + 106 + index * 58;
      context.font = '500 26px Tajawal, Segoe UI, sans-serif';
      context.fillStyle = '#344054';
      context.fillText(`${index + 1}. ${row.name}`, textX, rowY);
      context.textAlign = rtl ? 'left' : 'right';
      context.fillStyle = '#3A506B';
      context.font = '700 25px Tajawal, Segoe UI, sans-serif';
      context.fillText(row.value, valueX, rowY);
      context.textAlign = rtl ? 'right' : 'left';
    });
    y += boxHeight + 20;
  };

  section(
    labels.genes,
    report.top_genes.map((item) => ({
      name: `${item.name} — ${item.role}`,
      value: `${item.score.toFixed(1)}%`,
    }))
  );
  section(
    labels.archetypes,
    report.archetype_matches.map((item) => ({ name: item.name, value: `${item.score.toFixed(1)}%` }))
  );
  section(
    labels.quranValues,
    report.quran_values.map((item) => ({ name: item.name, value: item.score.toFixed(1) }))
  );
  section(
    labels.prophetTraits,
    report.prophet_traits.map((item) => ({ name: item.name, value: item.score.toFixed(1) }))
  );

  if (report.selected_activation) {
    const activationTop = y;
    const activationHeight = 242;
    context.fillStyle = 'rgba(255,255,255,0.76)';
    context.strokeStyle = 'rgba(197,168,128,0.75)';
    context.lineWidth = 2;
    context.beginPath();
    context.roundRect(edge, activationTop, canvas.width - edge * 2, activationHeight, 24);
    context.fill();
    context.stroke();

    context.textAlign = rtl ? 'right' : 'left';
    context.fillStyle = '#24364A';
    context.font = '700 31px Tajawal, Segoe UI, sans-serif';
    context.fillText(labels.activation, textX, activationTop + 54);
    context.font = '500 26px Tajawal, Segoe UI, sans-serif';
    context.fillStyle = '#344054';
    context.fillText(
      `${report.selected_activation.title} — ${report.selected_activation.channel}`,
      textX,
      activationTop + 108
    );
    context.font = '400 23px Tajawal, Segoe UI, sans-serif';
    context.fillStyle = '#667085';
    const body = report.selected_activation.body;
    const words = body.split(' ');
    let line = '';
    let bodyY = activationTop + 154;
    for (const word of words) {
      const candidate = line ? `${line} ${word}` : word;
      if (context.measureText(candidate).width > canvas.width - edge * 2 && line) {
        context.fillText(line, textX, bodyY);
        line = word;
        bodyY += 34;
      } else {
        line = candidate;
      }
    }
    if (line) context.fillText(line, textX, bodyY);
  }

  context.textAlign = 'center';
  context.font = '500 24px Tajawal, Segoe UI, sans-serif';
  context.fillStyle = '#667085';
  drawCenteredLine(labels.createdWith, 1840);
  context.textAlign = 'center';
  context.direction = rtl ? 'rtl' : 'ltr';
  context.fillStyle = '#3A506B';
  context.font = '700 25px Tajawal, Segoe UI, sans-serif';
  context.fillText(window.location.host || 'Miraati PersonaApp', 540, 1880);

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error('PNG generation failed'))), 'image/png');
  });
}
