import { useState, useCallback } from 'react'
import { Upload, FileText, Download, LogOut, CheckCircle, Loader, AlertCircle } from 'lucide-react'
import './App.css'

const API_BASE_URL = 'http://localhost:8000/api'

interface User {
  id: string
  name: string
  email: string
  picture?: string
}

interface ProcessedFile {
  id: string
  filename: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  formats?: string[]
  downloadUrls?: Record<string, string>
  error?: string
}

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [files, setFiles] = useState<ProcessedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFormats, setSelectedFormats] = useState<string[]>(['md', 'json'])

  const handleGoogleLogin = () => {
    window.location.href = `${API_BASE_URL}/auth/google`
  }

  const handleLogout = () => {
    setUser(null)
    setFiles([])
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    if (!user) return
    
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      file => file.type === 'application/pdf'
    )
    
    await uploadFiles(droppedFiles)
  }, [user])

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!user || !e.target.files) return
    
    const selectedFiles = Array.from(e.target.files).filter(
      file => file.type === 'application/pdf'
    )
    
    await uploadFiles(selectedFiles)
  }

  const uploadFiles = async (pdfFiles: File[]) => {
    const newFiles: ProcessedFile[] = pdfFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      filename: file.name,
      status: 'pending'
    }))
    
    setFiles(prev => [...prev, ...newFiles])
    
    for (const file of pdfFiles) {
      processFile(file)
    }
  }

  const processFile = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('formats', selectedFormats.join(','))
    
    try {
      setFiles(prev => prev.map(f => 
        f.filename === file.name ? { ...f, status: 'processing' } : f
      ))
      
      const response = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user?.id}`
        },
        body: formData
      })
      
      if (!response.ok) throw new Error('Failed to process file')
      
      const result = await response.json()
      
      setFiles(prev => prev.map(f => 
        f.filename === file.name ? { 
          ...f, 
          status: 'completed',
          formats: result.formats,
          downloadUrls: result.downloadUrls
        } : f
      ))
    } catch (error) {
      setFiles(prev => prev.map(f => 
        f.filename === file.name ? { 
          ...f, 
          status: 'error',
          error: 'Failed to process file'
        } : f
      ))
    }
  }

  const toggleFormat = (format: string) => {
    setSelectedFormats(prev => 
      prev.includes(format) 
        ? prev.filter(f => f !== format)
        : [...prev, format]
    )
  }

  const getStatusIcon = (status: ProcessedFile['status']) => {
    switch (status) {
      case 'processing':
        return <Loader className="animate-spin" size={20} />
      case 'completed':
        return <CheckCircle className="text-green-500" size={20} />
      case 'error':
        return <AlertCircle className="text-red-500" size={20} />
      default:
        return <FileText size={20} />
    }
  }

  if (!user) {
    return (
      <div className="app-container">
        <div className="login-container">
          <div className="logo">
            <FileText size={64} />
            <h1>PDFForge</h1>
            <p>Transforme seus PDFs em dados estruturados</p>
          </div>
          
          <button onClick={handleGoogleLogin} className="google-btn">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Entrar com Google
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-small">
          <FileText size={32} />
          <h2>PDFForge</h2>
        </div>
        
        <div className="user-info">
          {user.picture && (
            <img src={user.picture} alt={user.name} className="user-avatar" />
          )}
          <span>{user.name}</span>
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={20} />
          </button>
        </div>
      </header>

      <main className="app-main">
        <div className="upload-section">
          <h3>Enviar PDFs</h3>
          
          <div 
            className={`dropzone ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload size={48} />
            <p>Arraste seus PDFs aqui ou clique para selecionar</p>
            <input 
              type="file" 
              accept=".pdf" 
              multiple 
              onChange={handleFileInput}
              className="file-input"
            />
          </div>

          <div className="format-options">
            <h4>Formatos de saída:</h4>
            <div className="format-toggles">
              {['md', 'json', 'txt', 'html'].map(format => (
                <label key={format} className="toggle-label">
                  <input
                    type="checkbox"
                    checked={selectedFormats.includes(format)}
                    onChange={() => toggleFormat(format)}
                  />
                  <span className="toggle-text">{format.toUpperCase()}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {files.length > 0 && (
          <div className="files-section">
            <h3>Arquivos Processados</h3>
            <div className="files-list">
              {files.map(file => (
                <div key={file.id} className={`file-item ${file.status}`}>
                  <div className="file-info">
                    {getStatusIcon(file.status)}
                    <span className="filename">{file.filename}</span>
                  </div>
                  
                  {file.status === 'completed' && file.downloadUrls && (
                    <div className="download-links">
                      {Object.entries(file.downloadUrls).map(([format, url]) => (
                        <a 
                          key={format} 
                          href={url} 
                          className="download-btn"
                          download
                        >
                          <Download size={16} />
                          {format.toUpperCase()}
                        </a>
                      ))}
                    </div>
                  )}
                  
                  {file.status === 'error' && (
                    <span className="error-msg">{file.error}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
