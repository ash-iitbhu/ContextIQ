<template>
  <div class="chatbot-container">
    <h1>ContextIQ</h1>
    <div v-if="!isAuthenticated" class="auth-section">
      <div class="auth-tabs">
        <button :class="{active: authMode==='login'}" @click="authMode='login'">Login</button>
        <button :class="{active: authMode==='register'}" @click="authMode='register'">Register</button>
      </div>
      <form @submit.prevent="authMode==='login' ? login() : register()" class="auth-form">
        <input v-model="username" type="text" placeholder="Username" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <button class="modern-btn" type="submit">{{ authMode==='login' ? 'Login' : 'Register' }}</button>
      </form>
      <div v-if="authError" class="error">{{ authError }}</div>
    </div>
    <div v-else>
      <div v-if="!sessionId" class="input-section">
        <button class="logout-btn" @click="logout">Logout</button>
        <div class="modern-dropdown">
          <label for="source-select">Select Data Source</label>
          <select id="source-select" v-model="dataSource">
            <option value="youtube">YouTube URL</option>
            <option value="pdf">PDF File</option>
          </select>
        </div>
        <div class="modern-input">
          <input v-model="documentName" type="text" placeholder="Document Name" required />
        </div>
        <transition name="fade">
          <div v-if="dataSource === 'youtube'" class="modern-input">
            <input v-model="youtubeUrl" type="text" placeholder="Paste YouTube video URL here" />
          </div>
          <div v-else-if="dataSource === 'pdf'" class="modern-input">
            <input type="file" @change="onFileChange" accept=".pdf" />
          </div>
        </transition>
        <button class="modern-btn" @click="startChat" :disabled="loading">Start Chat</button>
        <div v-if="error" class="error">{{ error }}</div>
      </div>
      <div v-else class="chat-section">
        <button class="logout-btn" @click="logout">Logout</button>
        <div class="chat-window-modern">
          <div v-for="(msg, idx) in chatHistory" :key="idx" :class="['msg', msg.role]">
            <span>{{ msg.text }}</span>
          </div>
        </div>
        <form class="chat-form-modern" @submit.prevent="sendMessage">
          <input v-model="userInput" type="text" placeholder="Ask a question..." />
          <button type="submit" class="modern-btn">Send</button>
        </form>
        <button class="modern-btn outline" @click="resetChat">New Session</button>
      </div>
      <div v-if="showAuthModal" class="auth-modal">
        <div class="auth-modal-content">
          <span class="close" @click="showAuthModal = false">&times;</span>
          <div class="auth-tabs">
            <button :class="{active: authMode==='login'}" @click="authMode='login'">Login</button>
            <button :class="{active: authMode==='register'}" @click="authMode='register'">Register</button>
          </div>
          <form @submit.prevent="authMode==='login' ? login() : register()" class="auth-form">
            <input v-model="username" type="text" placeholder="Username" required />
            <input v-model="password" type="password" placeholder="Password" required />
            <button class="modern-btn" type="submit">{{ authMode==='login' ? 'Login' : 'Register' }}</button>
          </form>
          <div v-if="authError" class="error">{{ authError }}</div>
        </div>
      </div>
      <div v-if="loading" class="loading-spinner">
        <div class="spinner"></div>
        <div class="loading-text">Ingesting... Please wait</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const API_URL = 'http://localhost:8000'
const dataSource = ref('youtube')
const youtubeUrl = ref('')
const pdfFile = ref(null)
const sessionId = ref('')
const userInput = ref('')
const chatHistory = ref([])
const error = ref('')
const authMode = ref('login')
const username = ref('')
const password = ref('')
const authError = ref('')
const jwtToken = ref(localStorage.getItem('jwtToken') || '')
const isAuthenticated = computed(() => !!jwtToken.value)
const showAuthModal = ref(false)
const loading = ref(false)
const documentName = ref('')

watch(jwtToken, (newVal) => {
  if (newVal) {
    // On login, reset auth error and show ingestion/chat UI
    authError.value = ''
  } else {
    // On logout, reset session/chat
    sessionId.value = ''
    chatHistory.value = []
    error.value = ''
  }
})

onMounted(() => {
  // On page load, clear JWT and force logout
  jwtToken.value = ''
  localStorage.removeItem('jwtToken')
  sessionId.value = ''
  chatHistory.value = []
  error.value = ''
})

function onFileChange(e) {
  pdfFile.value = e.target.files[0]
}

async function register() {
  authError.value = ''
  try {
    const res = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    })
    const data = await res.json()
    if (res.ok) {
      authMode.value = 'login'
      authError.value = 'Registration successful. Please login.'
    } else {
      authError.value = data.detail || data.msg || 'Registration failed.'
    }
  } catch (e) {
    authError.value = 'Server error. Please try again.'
  }
}

async function login() {
  authError.value = ''
  try {
    const res = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    })
    const data = await res.json()
    if (res.ok && data.access_token) {
      jwtToken.value = data.access_token
      localStorage.setItem('jwtToken', data.access_token)
      authError.value = 'Login successful.'
      showAuthModal.value = false
    } else {
      authError.value = data.detail || 'Login failed.'
    }
  } catch (e) {
    authError.value = 'Server error. Please try again.'
  }
}

function logout() {
  jwtToken.value = ''
  localStorage.removeItem('jwtToken')
  sessionId.value = ''
  chatHistory.value = []
  error.value = ''
}

async function startChat() {
  error.value = ''
  loading.value = true
  const formData = new FormData()
  formData.append('document_name', documentName.value)
  if (dataSource.value === 'youtube' && youtubeUrl.value) formData.append('youtube_url', youtubeUrl.value)
  if (dataSource.value === 'pdf' && pdfFile.value) formData.append('pdf', pdfFile.value)
  try {
    const res = await fetch(`${API_URL}/ingest`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${jwtToken.value}` },
      body: formData
    })
    if (res.status === 401) {
      error.value = 'You must login/register first.'
      loading.value = false
      return
    }
    const data = await res.json()
    if (data.session_id) {
      sessionId.value = data.session_id
      chatHistory.value = []
    } else {
      error.value = data.error || 'Failed to ingest document.'
    }
  } catch (e) {
    error.value = 'Server error. Please try again.'
  }
  loading.value = false
}

async function sendMessage() {
  if (!userInput.value) return
  chatHistory.value.push({ role: 'user', text: userInput.value })
  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${jwtToken.value}`
      },
      body: JSON.stringify({ session_id: sessionId.value, message: userInput.value })
    })
    const data = await res.json()
    chatHistory.value.push({ role: 'bot', text: data.answer })
    userInput.value = ''
  } catch (e) {
    chatHistory.value.push({ role: 'bot', text: 'Error contacting backend.' })
  }
}

function resetChat() {
  sessionId.value = ''
  youtubeUrl.value = ''
  pdfFile.value = null
  chatHistory.value = []
  error.value = ''
  dataSource.value = 'youtube'
}
</script>

<style scoped>
.chatbot-container {
  max-width: 1500px;
  margin: 1rem auto;
  padding: 8rem 7rem;
  border-radius: 10px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  box-shadow: 0 8px 32px rgba(44,62,80,0.12);
  font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}

h1 {
  text-align: center;
  font-weight: 1500;
  color: #2d3a4a;
  margin-bottom: 3rem;
}

.input-section {
  display: flex;
  flex-direction: column;
  align-items: left;
}

.modern-dropdown {
  width: 114%;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.modern-dropdown label {
  font-size: 1rem;
  color: #2d3a4a;
  margin-bottom: 0.5rem;
  font-weight: 600;
}
.modern-dropdown select {
  width: 100%;
  padding: 0.7rem 1rem;
  border-radius: 8px;
  border: none;
  background: #eaf0fb;
  font-size: 1.1rem;
  color: #2d3a4a;
  box-shadow: 0 2px 8px rgba(44,62,80,0.08);
  transition: box-shadow 0.2s;
  outline: none;
}
.modern-dropdown select:focus {
  box-shadow: 0 0 0 2px #6c63ff33;
}

.modern-input input[type="text"], .modern-input input[type="file"] {
  width: 100%;
  padding: 0.7rem 1rem;
  border-radius: 8px;
  border: 1px solid #e0e6ed;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  background: #fff;
  transition: border 0.2s;
}
.modern-input input[type="text"]:focus {
  border: 1px solid #e0e6ed;
}

.modern-btn {
  padding: 0.7rem 2rem;
  border-radius: 8px;
  background: linear-gradient(90deg, #6661c0 0%, #47acce 100%);
  color: #fff;
  font-weight: 600;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(44,62,80,0.08);
  transition: background 0.2s;
}
.modern-btn.outline {
  background: linear-gradient(90deg, #6661c0 0%, #47acce 100%);
  color: #f0f0f4;
  padding: 1rem 1rem;
  margin-top: 1rem;
}
.modern-btn:hover {
  background: linear-gradient(90deg, #48c6ef 0%, #6c63ff 100%);
}

.error {
  color: #c00;
  margin-top: 1rem;
  font-weight: 500;
}

.chat-section {
  margin-top: 1rem;
}

.chat-window-modern {
  min-height: 300px;
  max-height: 400px;
  overflow-y: auto;
  background: #edf3f6;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(44,62,80,0.08);
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.msg {
  padding: 1rem 2rem;
  border-radius: 8px;
  max-width: 180%;
  word-break: break-word;
  font-size: 1.05rem;
  box-shadow: 0 1px 4px rgba(44,62,80,0.06);
}
.user {
  align-self: flex-end;
  background: linear-gradient(90deg, #6c63ff 0%, #48c6ef 100%);
  color: #fff;
}
.bot {
  align-self: flex-start;
  background: #eaf0fb;
  color: #2d3a4a;
}

.chat-form-modern {
  display: flex;
  gap: 0.7rem;
}
.chat-form-modern input {
  flex: 1;
  padding: 0.7rem 1rem;
  border-radius: 8px;
  border: 1px solid #e0e6ed;
  font-size: 1.1rem;
  background: #fff;
  transition: border 0.2s;
}
.chat-form-modern input:focus {
  border: 1.5px solid #6c63ff;
}
.chat-form-modern button {
  flex: none;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.auth-section {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  border-radius: 12px;
  background: #f9f9f9;
  box-shadow: 0 2px 8px rgba(44,62,80,0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.auth-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}
.auth-tabs button {
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  border: none;
  background: #eaf0fb;
  color: #2d3a4a;
  font-weight: 600;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}
.auth-tabs button.active {
  background: linear-gradient(90deg, #6661c0 0%, #47acce 100%);
  color: #fff;
}
.auth-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.auth-form input {
  padding: 0.7rem 1rem;
  border-radius: 8px;
  border: 1px solid #e0e6ed;
  font-size: 1.1rem;
  background: #fff;
}
.auth-form button {
  margin-top: 1rem;
}

.auth-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.auth-modal-content {
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  min-width: 320px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.2);
  position: relative;
}
.close {
  position: absolute;
  top: 8px;
  right: 12px;
  font-size: 1.5rem;
  cursor: pointer;
}

.logout-btn {
  position: absolute;
  top: 1rem;
  right: 2rem;
  z-index: 10;
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: background 0.2s;
}
.logout-btn:hover {
  background: #c0392b;
}
.chatbot-container {
  position: relative;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 2rem 0;
}
.spinner {
  width: 48px;
  height: 48px;
  border: 6px solid #e0e0e0;
  border-top: 6px solid #42b883;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.loading-text {
  font-size: 1.1rem;
  color: #42b883;
  font-weight: 500;
  letter-spacing: 0.5px;
}
</style>
