import { useCallback, useState } from 'react'

type Values = Record<string, string>
type Validators<T extends Values> = {
  [K in keyof T]?: (value: string, values: T) => string | undefined
}
type Errors<T extends Values> = Partial<Record<keyof T, string>>

/**
 * The validation timing from docs/ui/04-patterns.md, shared by the auth forms:
 * on blur for the field just left; on change *only* for a field already showing
 * an error, so mistakes clear as they're fixed rather than nagging mid-word;
 * and everything on submit.
 */
export function useAuthForm<T extends Values>(
  initial: T,
  validators: Validators<T>,
) {
  const [values, setValues] = useState<T>(initial)
  const [errors, setErrors] = useState<Errors<T>>({})

  const check = useCallback(
    (key: keyof T, next: T): string | undefined =>
      validators[key]?.(next[key], next),
    [validators],
  )

  const setValue = useCallback(
    (key: keyof T, value: string) => {
      setValues((prev) => {
        const next = { ...prev, [key]: value }
        setErrors((prevErrors) =>
          prevErrors[key] === undefined
            ? prevErrors
            : { ...prevErrors, [key]: check(key, next) },
        )
        return next
      })
    },
    [check],
  )

  const blur = useCallback(
    (key: keyof T) => {
      setErrors((prev) => ({ ...prev, [key]: check(key, values) }))
    },
    [check, values],
  )

  /** Runs every validator; returns the values only if all pass. */
  const validateAll = useCallback((): T | null => {
    const next: Errors<T> = {}
    for (const key of Object.keys(values) as (keyof T)[]) {
      next[key] = check(key, values)
    }
    setErrors(next)
    return Object.values(next).some(Boolean) ? null : values
  }, [check, values])

  /** Maps a server-side field error onto its field. */
  const setFieldError = useCallback((key: keyof T, message: string) => {
    setErrors((prev) => ({ ...prev, [key]: message }))
  }, [])

  return { values, errors, setValue, blur, validateAll, setFieldError }
}
