'use client';

import { useState, useEffect } from 'react';

interface ApiInfo {
  message: string;
  version: string;
  status: string;
  docs_url: string;
  project_info: {
    name: string;
    description: string;
    environment: string;
  };
}

const styles = {
  main: {
    display: 'flex',
    minHeight: '100vh',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
  },
  container: {
    maxWidth: '800px',
    width: '100%',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 'bold',
    marginBottom: '1.5rem',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: '1.25rem',
    marginBottom: '2rem',
    textAlign: 'center',
  },
  loading: {
    textAlign: 'center',
    padding: '1.5rem',
  },
  error: {
    textAlign: 'center',
    padding: '1.5rem',
    color: '#e53e3e',
  },
  errorDetails: {
    marginTop: '1rem',
    fontSize: '0.9rem',
    color: '#718096',
  },
  card: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '0.5rem',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e2e8f0',
    marginBottom: '2rem',
  },
  cardTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
  },
  statusText: {
    fontSize: '1.1rem',
    marginBottom: '0.5rem',
  },
  statusHealthy: {
    color: '#48bb78',
    fontWeight: 'bold',
  },
  statusUnhealthy: {
    color: '#e53e3e',
    fontWeight: 'bold',
  },
  infoRow: {
    marginBottom: '0.25rem',
  },
  link: {
    color: '#3182ce',
    textDecoration: 'underline',
  },
  debug: {
    marginTop: '2rem',
    padding: '1rem',
    backgroundColor: '#f7fafc',
    border: '1px solid #e2e8f0',
    borderRadius: '0.5rem',
    fontSize: '0.875rem',
    fontFamily: 'monospace',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-all',
  }
};

export default function Home() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...');
  const [apiInfo, setApiInfo] = useState<ApiInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);
  const [response, setResponse] = useState<string | null>(null);
  const [uptime, setUptime] = useState<number | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        // Try direct fetch to backend first
        const apiUrl = process.env.NEXT_PUBLIC_API_URL;

        // Log the API URL
        console.log('Attempting to connect to:', apiUrl);

        // Fetch health status with logging
        try {
          const healthResponse = await fetch(`${apiUrl}/api/v1/health`);
          const responseText = await healthResponse.text();
          setResponse(responseText); // Save raw response for debugging

          console.log('Health response:', responseText);

          // Only try to parse if we have a response
          if (responseText && responseText.trim()) {
            const healthData = JSON.parse(responseText);
            setApiStatus(healthData.status);
          } else {
            throw new Error('Empty response from API health endpoint');
          }
        } catch (error) {
          console.error('Error parsing health response:', error);
          const parseError = error as Error;
          throw new Error(`JSON parse error: ${parseError.message || 'Unknown error'}. Raw response: ${response}`);
        }

        // Fetch API root info with logging
        try {
          const infoResponse = await fetch(`${apiUrl}/api/v1`);
          const infoText = await infoResponse.text();

          console.log('Info response:', infoText);

          // Only try to parse if we have a response
          if (infoText && infoText.trim()) {
            const infoData = JSON.parse(infoText);
            setApiInfo(infoData);
          } else {
            throw new Error('Empty response from API info endpoint');
          }
        } catch (error) {
          console.error('Error parsing info response:', error);
          // Continue even if this fails, we already have health status
        }

        setLoading(false);
      } catch (error) {
        console.error('Error fetching API data:', error);
        setError('Failed to connect to API');
        setErrorDetails(`${error}`);
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  // Set up SSE for uptime stream
  useEffect(() => {
    // For production builds (with relative URLs), we don't include the API_URL
    // For local development, we use the absolute URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;

    // Use relative URL in production, absolute in development
    // Ensure the URL ends with a trailing slash to prevent redirects with protocol changes
    const streamUrl = `${apiUrl}/api/v1/uptime/stream`;
    console.log('Connecting to SSE stream at:', streamUrl);

    // Use withCredentials: false to ensure cross-origin requests work properly
    const eventSource = new EventSource(streamUrl, { withCredentials: false });

    eventSource.onmessage = (event) => {
      setUptime(parseInt(event.data, 10));
      console.log('Received uptime update:', event.data);
    };

    eventSource.onopen = () => {
      console.log('SSE connection opened successfully');
    };

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      // Don't close immediately on error, allow for automatic reconnection
      setTimeout(() => {
        console.log('Attempting to reconnect to SSE...');
      }, 2000);
    };

    return () => {
      console.log('Closing SSE connection');
      eventSource.close();
    };
  }, []);

  return (
    <main style={styles.main as React.CSSProperties}>
      <div style={styles.container as React.CSSProperties}>
        <h1 style={styles.title as React.CSSProperties}>SwissHacks</h1>
        <p style={styles.subtitle as React.CSSProperties}>Welcome to the SwissHacks web application!</p>

        {loading ? (
          <div style={styles.loading as React.CSSProperties}>Loading API data...</div>
        ) : error ? (
          <div style={styles.error as React.CSSProperties}>
            {error}
            {errorDetails && (
              <div style={styles.errorDetails as React.CSSProperties}>
                Details: {errorDetails}
              </div>
            )}
            {response && (
              <div style={styles.debug as React.CSSProperties}>
                Raw Response:
                {response}
              </div>
            )}
          </div>
        ) : (
          <div>
            <div style={styles.card as React.CSSProperties}>
              <h2 style={styles.cardTitle as React.CSSProperties}>API Status</h2>
              <p style={styles.statusText as React.CSSProperties}>
                Status: <span style={apiStatus === 'healthy' ? styles.statusHealthy : styles.statusUnhealthy as React.CSSProperties}>
                  {apiStatus}
                </span>
              </p>
              {apiInfo && (
                <>
                  <p style={styles.infoRow as React.CSSProperties}>Version: <span>{apiInfo.version}</span></p>
                  <p style={styles.infoRow as React.CSSProperties}>Message: <span>{apiInfo.message}</span></p>
                  <p style={styles.infoRow as React.CSSProperties}>
                    Documentation: <a
                      href={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/docs`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={styles.link as React.CSSProperties}
                    >
                      API Docs
                    </a>
                  </p>
                </>
              )}
            </div>

            {apiInfo && apiInfo.project_info && (
              <div style={styles.card as React.CSSProperties}>
                <h2 style={styles.cardTitle as React.CSSProperties}>Project Information</h2>
                <p style={styles.infoRow as React.CSSProperties}>Name: <span>{apiInfo.project_info.name}</span></p>
                <p style={styles.infoRow as React.CSSProperties}>Description: <span>{apiInfo.project_info.description}</span></p>
                <p style={styles.infoRow as React.CSSProperties}>Environment: <span style={{textTransform: 'capitalize'}}>{apiInfo.project_info.environment}</span></p>
              </div>
            )}

            <div style={styles.card as React.CSSProperties}>
              <h2 style={styles.cardTitle as React.CSSProperties}>Server Uptime</h2>
              <p style={styles.statusText as React.CSSProperties}>
                Current Uptime: <span style={styles.statusHealthy as React.CSSProperties}>
                  {uptime !== null ? `${uptime} seconds` : 'Connecting...'}
                </span>
              </p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}