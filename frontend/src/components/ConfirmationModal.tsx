import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';

interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  title,
  message,
  confirmLabel,
  cancelLabel,
  onConfirm,
  onCancel,
}) => {
  const cancelButtonRef = useRef<HTMLButtonElement>(null);
  const confirmButtonRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const onCancelRef = useRef(onCancel);

  useEffect(() => {
    onCancelRef.current = onCancel;
  }, [onCancel]);

  useEffect(() => {
    if (!isOpen) return undefined;

    previousFocusRef.current = document.activeElement as HTMLElement | null;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onCancelRef.current();
    };
    document.addEventListener('keydown', closeOnEscape);
    document.body.style.overflow = 'hidden';
    cancelButtonRef.current?.focus();

    return () => {
      document.removeEventListener('keydown', closeOnEscape);
      document.body.style.overflow = '';
      previousFocusRef.current?.focus();
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex min-h-screen items-center justify-center bg-ink/55 px-4 py-6"
      role="presentation"
      onClick={(event) => {
        if (event.target === event.currentTarget) onCancel();
      }}
    >
      <section
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirmation-title"
        aria-describedby="confirmation-message"
        className="w-full max-w-md rounded-soft border border-accent/70 bg-cream px-6 py-6 text-center text-ink shadow-soft-float sm:px-8 sm:py-8"
        onClick={(event) => event.stopPropagation()}
        onKeyDown={(event) => {
          if (event.key !== 'Tab') return;
          if (event.shiftKey && document.activeElement === cancelButtonRef.current) {
            event.preventDefault();
            confirmButtonRef.current?.focus();
          } else if (!event.shiftKey && document.activeElement === confirmButtonRef.current) {
            event.preventDefault();
            cancelButtonRef.current?.focus();
          }
        }}
      >
        <h2 id="confirmation-title" className="text-2xl font-semibold">
          {title}
        </h2>
        <p id="confirmation-message" className="mt-3 leading-relaxed text-muted">
          {message}
        </p>
        <div className="mt-6 flex flex-col-reverse justify-center gap-3 sm:flex-row">
          <button ref={cancelButtonRef} type="button" className="pill-button pill-button-secondary" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button ref={confirmButtonRef} type="button" className="pill-button pill-button-primary" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </section>
    </div>,
    document.body
  );
};

export default ConfirmationModal;
