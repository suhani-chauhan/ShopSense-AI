import { useCallback, useEffect, useState } from 'react'
import { deleteSavedProduct, listSavedProducts, saveProduct } from '../api/endpoints'
import type { SavedProduct, SaveProductRequest } from '../api/types'

interface UseSavedProductsResult {
  products: SavedProduct[]
  loading: boolean
  refresh: () => Promise<void>
  save: (payload: SaveProductRequest) => Promise<SavedProduct>
  remove: (id: number) => Promise<void>
}

export function useSavedProducts(): UseSavedProductsResult {
  const [products, setProducts] = useState<SavedProduct[]>([])
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const data = await listSavedProducts()
      setProducts(data)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const save = useCallback(async (payload: SaveProductRequest) => {
    const saved = await saveProduct(payload)
    setProducts((prev) => [saved, ...prev])
    return saved
  }, [])

  const remove = useCallback(async (id: number) => {
    await deleteSavedProduct(id)
    setProducts((prev) => prev.filter((p) => p.id !== id))
  }, [])

  return { products, loading, refresh, save, remove }
}
