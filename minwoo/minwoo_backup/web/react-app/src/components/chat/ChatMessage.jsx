const ChatMessage = ({ role = 'assistant', children }) => {
  const isUser = role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom: 12 }}>
      {!isUser && (
        <div style={{ width: 32, height: 32, borderRadius: 8, background: '#eef2ff', color: '#3730a3', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: 8 }}>💼</div>
      )}
      <div
        className="panel"
        style={{
          maxWidth: '72%',
          background: isUser ? '#111827' : '#ffffff',
          color: isUser ? '#fff' : 'inherit',
          borderColor: isUser ? '#111827' : '#e5e7eb',
          borderRadius: 12
        }}
      >
        {children}
      </div>
    </div>
  )
}

export default ChatMessage

