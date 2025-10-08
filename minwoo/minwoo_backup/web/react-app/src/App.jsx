import { StoreProvider } from './context/StoreContext'
import AppRouter from './router/AppRouter'
import './styles/global.css'

function App() {
  return (
    <StoreProvider>
      <AppRouter />
    </StoreProvider>
  )
}

export default App
