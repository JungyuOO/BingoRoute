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
    // 한글 IME 조합 중 Enter가 눌리면 중복 전송 방지
    const composing = e.isComposing || e.nativeEvent?.isComposing || e.keyCode === 229
    if (composing) return

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
