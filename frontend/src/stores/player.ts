/**
 * Audio player store
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { AudioFile } from '../types'
import { getStreamUrl } from '../api/client'

export const usePlayerStore = defineStore('player', () => {
    // State
    const playlist = ref<AudioFile[]>([])
    const currentIndex = ref<number>(-1)
    const isPlaying = ref(false)
    const currentTime = ref(0)
    const duration = ref(0)
    const volume = ref(1)

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

    // Watch volume changes
    watch(volume, (v) => {
        if (audio) {
            audio.volume = v
        }
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
    }
})
