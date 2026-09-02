import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { ConversationsProvider } from './context/ConversationsContext'
import { AppShell } from './components/layout/AppShell'
import { ChatPage } from './pages/ChatPage'
import { SavedProductsPage } from './pages/SavedProductsPage'
import { SettingsPage } from './pages/SettingsPage'
import { AboutPage } from './pages/AboutPage'

function App() {
  return (
    <ThemeProvider>
      <ConversationsProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<AppShell />}>
              <Route index element={<ChatPage />} />
              <Route path="c/:conversationId" element={<ChatPage />} />
              <Route path="saved" element={<SavedProductsPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="about" element={<AboutPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ConversationsProvider>
    </ThemeProvider>
  )
}

export default App
