/**
 * Axios API client for the AI Trip Planner backend.
 */
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'Something went wrong. Please try again.'
    return Promise.reject(new Error(typeof message === 'string' ? message : JSON.stringify(message)))
  },
)

export const planTrip = (payload) => api.post('/plan-trip', payload).then((r) => r.data)

export const saveTrip = (payload) => api.post('/save-trip', payload).then((r) => r.data)

export const getHistory = (params = {}) =>
  api.get('/history', { params }).then((r) => r.data)

export const getTrip = (id) => api.get(`/trip/${id}`).then((r) => r.data)

export const updateTrip = (id, payload) =>
  api.put(`/trip/${id}`, payload).then((r) => r.data)

export const deleteTrip = (id) => api.delete(`/trip/${id}`).then((r) => r.data)

export const duplicateTrip = (id) =>
  api.post(`/trip/${id}/duplicate`).then((r) => r.data)

export const reuseTrip = (id) => api.post(`/trip/${id}/reuse`).then((r) => r.data)

export const getWeather = (city) =>
  api.get('/weather', { params: { city } }).then((r) => r.data)

export const getPlaces = (destination, type) =>
  api.get('/places', { params: { destination, type } }).then((r) => r.data)

export const downloadTripPdf = async (id) => {
  const response = await api.get(`/trip/${id}/pdf`, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `trip_${id}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export default api
