import { useState } from 'react'

const ChatInput = ({ onSend }) => {
  const [text, setText] = useState('')

  const handleSend = () => {
    const value = text.trim()
    if (!value) return
    onSend(value)
    setText('')
  }

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="row" style={{ gap: 8 }}>
      <input
        className="input"
        style={{ flex: 1 }}
        placeholder="여행 계획에 대해 질문해보세요..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
      />
      <button className="brand-btn" onClick={handleSend} title="보내기">➤</button>
    </div>
  )
}

export default ChatInput

