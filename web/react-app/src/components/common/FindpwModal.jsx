import './FindpwModal.css'

const FindpwModal = ({ open, title, description, actions, onClose }) => {
  if (!open) return null

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal">
        <div className="header">
          <strong>{title}</strong>
        </div>
        <div className="content">
          {description && (
            <p className="muted" style={{ marginTop: 0, whiteSpace: 'pre-line' }}>
              {description}
            </p>
          )}
          <div className="row" style={{ justifyContent: 'flex-end', gap: 8 }}>
            {actions?.map(({ label, variant = 'ghost', onClick, type = 'button', disabled = false }) => (
              <button
                key={label}
                type={type}
                className={variant === 'brand' ? 'brand-btn' : 'ghost-btn'}
                onClick={onClick}
                disabled={disabled}
              >
                {label}
              </button>
            ))}
            {!actions && (
              <button className="brand-btn" onClick={onClose}>확인</button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default FindpwModal
