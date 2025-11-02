const ChatMessage = ({ role = 'assistant', children }) => {
  const isUser = role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', marginBottom: 12 }}>
      {!isUser && (
        <div style={{ width: 30, height: 30, borderRadius: 8, background: '#eef2ff', color: '#3730a3', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: 10 }}>🤖</div>
      )}
      <div
        className="panel"
        style={{
          maxWidth: '79%',
          background: isUser ? '#FBBE0E' : '#ffffff',
          color: isUser ? '#fff' : 'inherit',
          borderColor: isUser ? '#FBBE0E' : '#e5e7eb',
          borderRadius: 15
        }}
      >
        {children}
      </div>
    </div>
  )
}

export default ChatMessage

