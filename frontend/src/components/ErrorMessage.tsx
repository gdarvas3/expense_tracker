import type { ReactElement } from 'react'

interface ErrorMessageProps {
  message: string | null
}

export function ErrorMessage({ message }: ErrorMessageProps): ReactElement | null {
  if (message === null) {
    return null
  }
  return (
    <p role="alert" className="error">
      {message}
    </p>
  )
}
