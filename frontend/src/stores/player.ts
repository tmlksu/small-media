/**
 * Audio player store with session persistence
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { AudioFile } from '../types'
import { getStreamUrl } from '../api/client'

// Session storage keys
const STORAGE_KEYS = {
    playlist: 'player:playlist',
    currentIndex: 'player:currentIndex',
    currentTime: 'player:currentTime',
    volume: 'player:volume',
}

// Load persisted state from sessionStorage
function loadPersistedState() {
    try {
        const playlist = sessionStorage.getItem(STORAGE_KEYS.playlist)
        const currentIndex = sessionStorage.getItem(STORAGE_KEYS.currentIndex)
        const currentTime = sessionStorage.getItem(STORAGE_KEYS.currentTime)
        const volume = sessionStorage.getItem(STORAGE_KEYS.volume)

        return {
            playlist: playlist ? JSON.parse(playlist) : [],
            currentIndex: currentIndex ? parseInt(currentIndex, 10) : -1,
            currentTime: currentTime ? parseFloat(currentTime) : 0,
            volume: volume ? parseFloat(volume) : 1,
        }
    } catch {
        return { playlist: [], currentIndex: -1, currentTime: 0, volume: 1 }
    }
}

export const usePlayerStore = defineStore('player', () => {
    // Load persisted state
    const persisted = loadPersistedState()

    // State
    const playlist = ref<AudioFile[]>(persisted.playlist)
    const currentIndex = ref<number>(persisted.currentIndex)
    const isPlaying = ref(false)
    const currentTime = ref(persisted.currentTime)
    const duration = ref(0)
    const volume = ref(persisted.volume)

    // Audio element (created on demand)
    let audio: HTMLAudioElement | null = null

    // Getters
    const currentTrack = computed(() => {
        if (currentIndex.value >= 0 && currentIndex.value < playlist.value.length) {
            return playlist.value[currentIndex.value]
        }
        return null
    })

    const hasNext = computed(() => currentIndex.value < playlist.value.length - 1)
    const hasPrevious = computed(() => currentIndex.value > 0)
    const progress = computed(() => (duration.value > 0 ? currentTime.value / duration.value : 0))

    // Initialize audio element
    function getAudio(): HTMLAudioElement {
        if (!audio) {
            audio = new Audio()
            audio.volume = volume.value

            // Event listeners
            audio.addEventListener('timeupdate', () => {
                currentTime.value = audio!.currentTime
            })

            audio.addEventListener('durationchange', () => {
                duration.value = audio!.duration
            })

            audio.addEventListener('ended', () => {
                if (hasNext.value) {
                    next()
                } else {
                    isPlaying.value = false
                }
            })

            audio.addEventListener('play', () => {
                isPlaying.value = true
                updateMediaSession()
            })

            audio.addEventListener('pause', () => {
                isPlaying.value = false
            })
        }
        return audio
    }

    // Update Media Session API (for lock screen controls)
    function updateMediaSession() {
        if ('mediaSession' in navigator) {
            navigator.mediaSession.metadata = new MediaMetadata({
                title: 'Small Media',
                artist: '',
                album: '',
            })

            navigator.mediaSession.setActionHandler('play', () => play())
            navigator.mediaSession.setActionHandler('pause', () => pause())
            navigator.mediaSession.setActionHandler('previoustrack', () => previous())
            navigator.mediaSession.setActionHandler('nexttrack', () => next())
        }
    }

    // Actions
    function setPlaylist(files: AudioFile[], startIndex = 0) {
        playlist.value = files
        currentIndex.value = startIndex
        loadAndPlay()
    }

    function loadAndPlay() {
        const track = currentTrack.value
        if (!track) return

        const audioEl = getAudio()
        audioEl.src = getStreamUrl(track.path)
        audioEl.load()
        audioEl.play()
    }

    function play() {
        const audioEl = getAudio()
        if (audioEl.src) {
            audioEl.play()
        } else if (currentTrack.value) {
            loadAndPlay()
        }
    }

    function pause() {
        getAudio().pause()
    }

    function toggle() {
        if (isPlaying.value) {
            pause()
        } else {
            play()
        }
    }

    function next() {
        if (hasNext.value) {
            currentIndex.value++
            loadAndPlay()
        }
    }

    function previous() {
        if (hasPrevious.value) {
            currentIndex.value--
            loadAndPlay()
        }
    }

    function seek(time: number) {
        const audioEl = getAudio()
        if (audioEl.src) {
            audioEl.currentTime = time
        }
    }

    function seekToProgress(progress: number) {
        seek(progress * duration.value)
    }

    function setVolume(v: number) {
        volume.value = Math.max(0, Math.min(1, v))
        if (audio) {
            audio.volume = volume.value
        }
    }

    // Watch for state changes and persist to sessionStorage
    watch(playlist, (p) => {
        sessionStorage.setItem(STORAGE_KEYS.playlist, JSON.stringify(p))
    }, { deep: true })

    watch(currentIndex, (i) => {
        sessionStorage.setItem(STORAGE_KEYS.currentIndex, String(i))
    })

    // Throttle currentTime saves (every 5 seconds)
    let lastTimeSave = 0
    watch(currentTime, (t) => {
        const now = Date.now()
        if (now - lastTimeSave > 5000) {
            sessionStorage.setItem(STORAGE_KEYS.currentTime, String(t))
            lastTimeSave = now
        }
    })

    // Watch volume changes
    watch(volume, (v) => {
        if (audio) {
            audio.volume = v
        }
        sessionStorage.setItem(STORAGE_KEYS.volume, String(v))
    })

    function playIndex(index: number) {
        if (index >= 0 && index < playlist.value.length) {
            currentIndex.value = index
            loadAndPlay()
        }
    }

    function removeFromPlaylist(index: number) {
        if (index >= 0 && index < playlist.value.length) {
            playlist.value.splice(index, 1)
            // Adjust current index if needed
            if (index < currentIndex.value) {
                currentIndex.value--
            } else if (index === currentIndex.value) {
                // Current track removed, play next if available
                if (currentIndex.value >= playlist.value.length) {
                    currentIndex.value = playlist.value.length - 1
                }
                if (playlist.value.length > 0) {
                    loadAndPlay()
                } else {
                    // Playlist empty
                    currentIndex.value = -1
                    getAudio().pause()
                }
            }
        }
    }

    /**
     * Resume playback from persisted state (after page reload)
     * Call this after the app is mounted
     */
    function resumePlayback() {
        if (playlist.value.length > 0 && currentIndex.value >= 0) {
            const track = currentTrack.value
            if (track) {
                const audioEl = getAudio()
                audioEl.src = getStreamUrl(track.path)
                audioEl.load()

                // Seek to saved position once metadata is loaded
                const savedTime = persisted.currentTime
                if (savedTime > 0) {
                    audioEl.addEventListener('loadedmetadata', function onLoaded() {
                        audioEl.currentTime = savedTime
                        audioEl.removeEventListener('loadedmetadata', onLoaded)
                    })
                }
                // Don't auto-play - wait for user interaction
            }
        }
    }

    return {
        // State
        playlist,
        currentIndex,
        isPlaying,
        currentTime,
        duration,
        volume,

        // Getters
        currentTrack,
        hasNext,
        hasPrevious,
        progress,

        // Actions
        setPlaylist,
        play,
        pause,
        toggle,
        next,
        previous,
        seek,
        seekToProgress,
        setVolume,
        playIndex,
        removeFromPlaylist,
        resumePlayback,
    }
})
