import { useState, useEffect } from 'react';

export default function Home() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...');
  
  useEffect(() => {
    async function checkApiHealth() {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/health`);
        const data = await response.json();
        setApiStatus(data.status);
      } catch (error) {
        console.error('Error checking API health:', error);
        setApiStatus('Error connecting to API');
      }
    }
    
    checkApiHealth();
  }, []);
  
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-6">SwissHacks</h1>
      <p className="text-xl mb-4">Welcome to the SwissHacks web application!</p>
      
      <div className="mt-8 p-6 border rounded-lg bg-white/5 shadow-md">
        <h2 className="text-2xl font-semibold mb-4">API Status</h2>
        <p className="text-lg">
          Backend API: <span className={apiStatus === 'healthy' ? 'text-green-500' : 'text-red-500'}>
            {apiStatus}
          </span>
        </p>
      </div>
    </main>
  )
}