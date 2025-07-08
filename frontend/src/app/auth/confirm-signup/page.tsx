import Link from 'next/link'

export default function ConfirmSignupPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            AI SDR Agent
          </h1>
          <h2 className="mt-6 text-2xl font-bold tracking-tight text-gray-900">
            Check your email
          </h2>
          <div className="mt-4 rounded-md bg-blue-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3 flex-1 md:flex md:justify-between">
                <p className="text-sm text-blue-700">
                  We've sent a confirmation email to your address. Please click the link in the email to verify your account.
                </p>
              </div>
            </div>
          </div>
          <p className="mt-6 text-base text-gray-600">
            Once you've confirmed your email, you can log in to start using the AI SDR Agent.
          </p>
          <div className="mt-6">
            <Link href="/auth/login" className="font-medium text-blue-600 hover:text-blue-500">
              Return to login page
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
} 