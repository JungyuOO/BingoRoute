const QuickReplies = ({ options = [], onSelect }) => {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
      {options.map((label) => (
        <button
          key={label}
          className="chip"
          style={{ cursor: 'pointer' }}
          onClick={() => onSelect(label)}
        >
          {label}
        </button>
      ))}
    </div>
  )
}

export default QuickReplies

