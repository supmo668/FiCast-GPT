"use client";
// src/app/pages/login.tsx
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Image from 'next/image'; // Import for the Google icon
import GoogleButton from 'react-google-button'

const Login = () => {
  const { user, authResponse, loading, signIn } = useAuth();
  const router = useRouter();
  const [showModal, setShowModal] = useState(false);

  // Log the login page render for debugging
  // Redirect to profile if user is authenticated
  useEffect(() => {
    if (!loading && user) {
      console.log('User authenticated, redirecting to profile...'); // Log before redirection
      router.push('/profile');
    }
  }, [user, loading, router]);

  // Show modal when there is an authentication response
  useEffect(() => {
    if (authResponse) {
      setShowModal(true);
    }
  }, [authResponse]);

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-slate-900 text-white">
      <h1 className="text-3xl mb-6">Login to FiCast</h1>

      {/* Standard Google Sign-In Button */}
      <GoogleButton onClick={signIn} />

      {/* Authentication Status Modal */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded shadow-lg max-w-lg w-full">
            <h2 className="text-xl mb-4">Authentication Status</h2>
            <p>{authResponse}</p>
            <button
              onClick={() => setShowModal(false)}
              className="mt-4 bg-blue-500 text-white px-4 py-2 rounded"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;
