import Header from './Header'
import LoginRequiredModal from './auth/LoginRequiredModal'

const Layout = ({ children }) => {
  return (
    <div className="br-layout">
      <Header />
      <main id="outlet">
        {children}
      </main>
      <LoginRequiredModal />
    </div>
  )
}

export default Layout
