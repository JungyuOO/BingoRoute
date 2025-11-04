import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react'
import { fetchJjimList } from '../services/jjimService'
import {
  fetchTrips as fetchTripPlans,
  createTrip as createTripPlan,
  updateTripPlan as patchTripPlan,
  deleteTrip as deleteTripPlan,
  createItinerary,
  deleteItinerary,
} from '../services/tripService'
import { validateSession } from '../services/authService'

const StoreContext = createContext()

const defaultTravelDate = () => new Date().toISOString().slice(0, 10)

const normalizeTrip = (trip) => {
  if (!trip) return null

  const itineraries = Array.isArray(trip.itineraries)
    ? [...trip.itineraries].sort((a, b) => (a.seq ?? 0) - (b.seq ?? 0))
    : []

  return {
    id: trip.trip_id,
    title: trip.trip_title,
    status: trip.status,
    travelDate: trip.travel_date,
    startDate: trip.travel_date,
    endDate: trip.travel_date,
    createdAt: trip.created_at,
    updatedAt: trip.updated_at,
    itineraries,
    destinations: itineraries.map((item) => item.content_id),
    raw: trip,
  }
}

const toContentId = (destination) => {
  if (destination === null || destination === undefined) return null
  if (typeof destination === 'string' || typeof destination === 'number') return destination
  return destination.id ?? destination.content_id ?? null
}

export const useStore = () => {
  const context = useContext(StoreContext)
  if (!context) {
    throw new Error('useStore must be used within a StoreProvider')
  }
  return context
}

export const StoreProvider = ({ children }) => {
  const [users, setUsers] = useState([])
  const [session, setSession] = useState(null)
  const [wishlist, setWishlist] = useState([])
  const [trips, setTrips] = useState([])
  const [tripsLoading, setTripsLoading] = useState(false)
  const [tripError, setTripError] = useState(null)
  const [loginRequired, setLoginRequired] = useState(false)
  const [storageHydrated, setStorageHydrated] = useState(false)

  const tripsRef = useRef([])
  const pendingTripUpdateTimers = useRef(new Map())

  useEffect(() => {
    tripsRef.current = trips
  }, [trips])

  useEffect(() => () => {
    pendingTripUpdateTimers.current.forEach((timer) => clearTimeout(timer))
    pendingTripUpdateTimers.current.clear()
  }, [])

  const refreshTrips = useCallback(async () => {
    if (!session?.user_id) {
      setTrips([])
      return
    }

    setTripsLoading(true)
    setTripError(null)

    try {
      const remote = await fetchTripPlans(session.user_id)
      const normalized = remote
        .map(normalizeTrip)
        .filter(Boolean)

      setTrips(normalized)
    } catch (error) {
      console.error('여행 계획을 불러오지 못했습니다:', error)
      setTripError(error)
    } finally {
      setTripsLoading(false)
    }
  }, [session?.user_id])

  const addDestinationToTrip = useCallback(
    async ({ tripId, tripTitle, destination, travelDate } = {}) => {
      if (!session?.user_id) {
        setLoginRequired(true)
        throw new Error('로그인이 필요합니다.')
      }

      const contentId = toContentId(destination)
      if (!contentId) {
        throw new Error('destination 식별자가 필요합니다.')
      }

      try {
        if (tripId) {
          const currentTrip = tripsRef.current.find((trip) => String(trip.id) === String(tripId))
          const currentSeqs = (currentTrip?.itineraries || [])
            .map((item) => item.seq)
            .filter((seq) => typeof seq === 'number')
          const nextSeq = currentSeqs.length > 0 ? Math.max(...currentSeqs) + 1 : 1

          await createItinerary(tripId, {
            seq: nextSeq,
            content_id: String(contentId),
          })
        } else {
          const payload = {
            status: 'PLANNED',
            trip_title: tripTitle || '',
            travel_date: travelDate || defaultTravelDate(),
            itineraries: [
              {
                seq: 1,
                content_id: String(contentId),
              },
            ],
          }

          await createTripPlan(session.user_id, payload)
        }

        await refreshTrips()
      } catch (error) {
        console.error('여행지를 추가하지 못했습니다:', error)
        throw error
      }
    },
    [refreshTrips, session?.user_id],
  )

  const clearTrips = useCallback(async () => {
    if (!session?.user_id) {
      setTrips([])
      return
    }

    const deletions = tripsRef.current.map((trip) =>
      deleteTripPlan(session.user_id, trip.id).catch((error) => {
        console.error('여행 계획 삭제 실패:', error)
      }),
    )

    await Promise.all(deletions)
    await refreshTrips()
  }, [refreshTrips, session?.user_id])

  const updateTrip = useCallback(
    (tripId, updates) => {
      setTrips((prevTrips) =>
        prevTrips.map((trip) =>
          trip.id === tripId
            ? {
                ...trip,
                ...(updates.title !== undefined ? { title: updates.title } : {}),
                ...(updates.startDate !== undefined ? { startDate: updates.startDate } : {}),
                ...(updates.endDate !== undefined ? { endDate: updates.endDate } : {}),
              }
            : trip,
        ),
      )

      if (!session?.user_id) return

      const timer = pendingTripUpdateTimers.current.get(tripId)
      if (timer) clearTimeout(timer)

      const newTimer = setTimeout(async () => {
        pendingTripUpdateTimers.current.delete(tripId)
        const currentTrip = tripsRef.current.find((trip) => trip.id === tripId)
        if (!currentTrip) return

        const payload = {}

        if (currentTrip.title !== undefined) {
          const trimmed = typeof currentTrip.title === 'string' ? currentTrip.title.trim() : currentTrip.title
          payload.trip_title = trimmed || ''
        }

        const candidateDate = currentTrip.startDate || currentTrip.travelDate
        if (candidateDate) {
          payload.travel_date = candidateDate || defaultTravelDate()
        }

        if (Object.keys(payload).length === 0) return

        try {
          await patchTripPlan(session.user_id, tripId, payload)
          await refreshTrips()
        } catch (error) {
          console.error('여행 계획 업데이트 실패:', error)
        }
      }, 600)

      pendingTripUpdateTimers.current.set(tripId, newTimer)
    },
    [refreshTrips, session?.user_id],
  )

  const removeDestinationFromTrip = useCallback(
    async (tripId, seq) => {
      if (!session?.user_id) {
        setLoginRequired(true)
        return
      }

      try {
        await deleteItinerary(tripId, seq)
        await refreshTrips()
      } catch (error) {
        console.error('여행 일정을 삭제하지 못했습니다:', error)
        throw error
      }
    },
    [refreshTrips, session?.user_id],
  )

  const deleteTrip = useCallback(
    async (tripId) => {
      if (!session?.user_id) {
        setLoginRequired(true)
        return
      }

      try {
        await deleteTripPlan(session.user_id, tripId)
        await refreshTrips()
      } catch (error) {
        console.error('여행 계획 삭제 실패:', error)
        throw error
      }
    },
    [refreshTrips, session?.user_id],
  )

  const mergeTrips = useCallback(
    async (targetTripId, sourceTripIds = []) => {
      if (!session?.user_id) {
        setLoginRequired(true)
        return
      }

      if (!targetTripId || !Array.isArray(sourceTripIds) || sourceTripIds.length === 0) return

      const targetTrip = tripsRef.current.find((trip) => String(trip.id) === String(targetTripId))
      if (!targetTrip) return

      const existingSeqs = (targetTrip.itineraries || [])
        .map((item) => item.seq)
        .filter((seq) => typeof seq === 'number')
      let nextSeq = existingSeqs.length > 0 ? Math.max(...existingSeqs) + 1 : 1

      const existingContentIds = new Set((targetTrip.itineraries || []).map((item) => item.content_id))

      try {
        for (const sourceId of sourceTripIds) {
          const sourceTrip = tripsRef.current.find((trip) => String(trip.id) === String(sourceId))
          if (!sourceTrip) continue

          for (const itinerary of sourceTrip.itineraries || []) {
            if (existingContentIds.has(itinerary.content_id)) continue

            await createItinerary(targetTripId, {
              seq: nextSeq++,
              content_id: String(itinerary.content_id),
              visit_date: itinerary.visit_date || undefined,
              stay_time: itinerary.stay_time || undefined,
            })

            existingContentIds.add(itinerary.content_id)
          }

          await deleteTripPlan(session.user_id, sourceId)
        }

        await refreshTrips()
      } catch (error) {
        console.error('여행 계획 병합 실패:', error)
        throw error
      }
    },
    [refreshTrips, session?.user_id],
  )

  const replanTrip = useCallback(
    async (tripId) => {
      if (!session?.user_id) {
        setLoginRequired(true)
        return
      }

      const trip = tripsRef.current.find((item) => item.id === tripId)
      if (!trip) return

      const baseTitle = typeof trip.title === 'string' ? trip.title : ''
      const newTitle = baseTitle.includes('(재계획)') ? baseTitle : `${baseTitle} (재계획)`

      try {
        await patchTripPlan(session.user_id, tripId, {
          trip_title: newTitle,
          travel_date: defaultTravelDate(),
        })
        await refreshTrips()
      } catch (error) {
        console.error('여행 계획을 다시 계획하지 못했습니다:', error)
        throw error
      }
    },
    [refreshTrips, session?.user_id],
  )

  useEffect(() => {
    setUsers(JSON.parse(localStorage.getItem('br_users') || '[]'))
    const storedSession = JSON.parse(localStorage.getItem('br_session') || 'null')
    setSession(storedSession)
    setWishlist(JSON.parse(localStorage.getItem('br_wishlist') || '[]'))
    setStorageHydrated(true)
    let cancelled = false

    const hydrateFromStorage = async () => {
      const storedUsers = JSON.parse(localStorage.getItem('br_users') || '[]')
      const storedWishlist = JSON.parse(localStorage.getItem('br_wishlist') || '[]')
      const storedTrips = JSON.parse(localStorage.getItem('br_trips') || '[]')
      const storedSession = JSON.parse(localStorage.getItem('br_session') || 'null')

      if (!cancelled) {
        setUsers(storedUsers)
        setWishlist(storedWishlist)
        setTrips(storedTrips)
      }

      if (storedSession?.access) {
        try {
          const data = await validateSession(storedSession.access)
          if (!cancelled) {
            setSession({ ...data.user, access: storedSession.access })
          }
        } catch (error) {
          if (cancelled) return
          if (error?.status === 401) {
            console.warn('Stored session is no longer valid. Clearing it.', error)
            setSession(null)
            localStorage.removeItem('br_session')
          } else {
            console.warn('Unable to verify stored session. Keeping cached session for now.', error)
            setSession(storedSession)
          }
        }
      } else if (!cancelled) {
        setSession(storedSession)
      }

      if (!cancelled) {
        setStorageHydrated(true)
      }
    }

    hydrateFromStorage()

    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!storageHydrated) return
    localStorage.setItem('br_users', JSON.stringify(users))
  }, [users, storageHydrated])

  useEffect(() => {
    if (!storageHydrated) return
    if (session === null) {
      localStorage.removeItem('br_session')
    } else {
      localStorage.setItem('br_session', JSON.stringify(session))
    }
  }, [session, storageHydrated])

  useEffect(() => {
    if (!storageHydrated) return
    localStorage.setItem('br_wishlist', JSON.stringify(wishlist))
  }, [wishlist, storageHydrated])

  useEffect(() => {
    if (!storageHydrated) return
    refreshTrips()
  }, [refreshTrips, storageHydrated])

  useEffect(() => {
    let cancelled = false

    const syncWishlist = async () => {
      if (!session?.user_id) {
        setWishlist([])
        return
      }
      try {
        const remoteWishlist = await fetchJjimList(session.user_id)
        if (!cancelled) {
          setWishlist(remoteWishlist)
        }
      } catch (error) {
        console.error('찜 목록을 불러오지 못했습니다:', error)
      }
    }

    syncWishlist()

    return () => {
      cancelled = true
    }
  }, [session?.user_id])

  const value = {
    users,
    setUsers,
    session,
    setSession,
    wishlist,
    setWishlist,
    trips,
    setTrips,
    tripsLoading,
    tripError,
    addDestinationToTrip,
    clearTrips,
    updateTrip,
    removeDestinationFromTrip,
    deleteTrip,
    mergeTrips,
    replanTrip,
    loginRequired,
    setLoginRequired,
    refreshTrips,
  }

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  )
}
