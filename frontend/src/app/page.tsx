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
    background: 'linear-gradient(135deg, #f5f7fa 0%, #e4ebf5 100%)',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  container: {
    maxWidth: '900px',
    width: '100%',
  },
  header: {
    marginBottom: '3rem',
    textAlign: 'center',
  },
  title: {
    fontSize: '3.5rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    textAlign: 'center',
    background: 'linear-gradient(135deg, #1a365d 0%, #2563eb 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    textShadow: '0 1px 2px rgba(0,0,0,0.1)',
  },
  subtitle: {
    fontSize: '1.25rem',
    color: '#4a5568',
    marginBottom: '2rem',
    textAlign: 'center',
    maxWidth: '600px',
    margin: '0 auto',
  },
  loading: {
    textAlign: 'center',
    padding: '3rem',
    fontSize: '1.25rem',
    color: '#4a5568',
    animation: 'pulse 2s infinite ease-in-out',
  },
  error: {
    textAlign: 'center',
    padding: '1.5rem',
    color: '#e53e3e',
    backgroundColor: 'rgba(254, 226, 226, 0.5)',
    borderRadius: '0.5rem',
    border: '1px solid rgba(229, 62, 62, 0.3)',
  },
  errorDetails: {
    marginTop: '1rem',
    fontSize: '0.9rem',
    color: '#718096',
  },
  cardGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '1.5rem',
  },
  card: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '1rem',
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.05)',
    border: '1px solid rgba(226, 232, 240, 0.8)',
    marginBottom: '1.5rem',
    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
    ':hover': {
      transform: 'translateY(-5px)',
      boxShadow: '0 15px 30px rgba(0, 0, 0, 0.1)',
    },
  },
  cardTitle: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    marginBottom: '1rem',
    color: '#1a365d',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  statusBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '0.25rem 0.75rem',
    borderRadius: '9999px',
    fontSize: '0.875rem',
    fontWeight: 'medium',
    marginLeft: 'auto',
  },
  statusText: {
    fontSize: '1.1rem',
    marginBottom: '1rem',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  statusHealthy: {
    color: '#48bb78',
    fontWeight: 'bold',
    display: 'inline-flex',
    alignItems: 'center',
  },
  statusUnhealthy: {
    color: '#e53e3e',
    fontWeight: 'bold',
  },
  infoRow: {
    marginBottom: '0.75rem',
    display: 'flex',
    flexDirection: 'column',
  },
  infoLabel: {
    fontSize: '0.875rem',
    color: '#718096',
    marginBottom: '0.25rem',
  },
  infoValue: {
    fontWeight: 'medium',
    color: '#2d3748',
  },
  link: {
    color: '#3182ce',
    textDecoration: 'none',
    fontWeight: 'medium',
    transition: 'color 0.2s ease',
    ':hover': {
      color: '#2c5282',
      textDecoration: 'underline',
    },
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
  },
  uptimeValue: {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#48bb78',
    display: 'block',
    margin: '1rem 0',
    textAlign: 'center',
  },
  iconContainer: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '2rem',
    height: '2rem',
    borderRadius: '0.5rem',
    marginRight: '0.5rem',
    backgroundColor: 'rgba(49, 130, 206, 0.1)',
  },
  footer: {
    marginTop: '3rem',
    textAlign: 'center',
    fontSize: '0.875rem',
    color: '#718096',
  }
};

// Simple icons for decoration
const Icons = {
  Status: () => (
    <div style={styles.iconContainer as React.CSSProperties}>
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#3182ce" viewBox="0 0 16 16">
        <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
        <path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"/>
      </svg>
    </div>
  ),
  Project: () => (
    <div style={styles.iconContainer as React.CSSProperties}>
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#3182ce" viewBox="0 0 16 16">
        <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1H7zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
        <path fillRule="evenodd" d="M5.216 14A2.238 2.238 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.325 6.325 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1h4.216z"/>
        <path d="M4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/>
      </svg>
    </div>
  ),
  Time: () => (
    <div style={styles.iconContainer as React.CSSProperties}>
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#3182ce" viewBox="0 0 16 16">
        <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
        <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
      </svg>
    </div>
  ),
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

  // Format uptime to show days, hours, minutes, seconds
  const formatUptime = (seconds: number | null) => {
    if (seconds === null) return 'Connecting...';
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    const parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    parts.push(`${remainingSeconds}s`);
    
    return parts.join(' ');
  };

  return (
    <main style={styles.main as React.CSSProperties}>
      <div style={styles.container as React.CSSProperties}>
        <div style={styles.header as React.CSSProperties}>
          <h1 style={styles.title as React.CSSProperties}>SwissHacks</h1>
          <p style={styles.subtitle as React.CSSProperties}>
            Welcome to the SwissHacks platform - your gateway to innovative Swiss hackathons and tech events
          </p>
        </div>

        {loading ? (
          <div style={styles.loading as React.CSSProperties}>
            Loading API data...
          </div>
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
          <>
            <div style={styles.cardGrid as React.CSSProperties}>
              <div style={styles.card as React.CSSProperties}>
                <h2 style={styles.cardTitle as React.CSSProperties}>
                  <Icons.Status />
                  API Status
                  {apiStatus === 'healthy' ? (
                    <span style={{...styles.statusBadge as React.CSSProperties, backgroundColor: 'rgba(72, 187, 120, 0.1)', color: '#48bb78'}}>
                      Online
                    </span>
                  ) : (
                    <span style={{...styles.statusBadge as React.CSSProperties, backgroundColor: 'rgba(229, 62, 62, 0.1)', color: '#e53e3e'}}>
                      Offline
                    </span>
                  )}
                </h2>
                {apiInfo && (
                  <>
                    <div style={styles.infoRow as React.CSSProperties}>
                      <span style={styles.infoLabel as React.CSSProperties}>Version</span>
                      <span style={styles.infoValue as React.CSSProperties}>{apiInfo.version}</span>
                    </div>
                    <div style={styles.infoRow as React.CSSProperties}>
                      <span style={styles.infoLabel as React.CSSProperties}>Message</span>
                      <span style={styles.infoValue as React.CSSProperties}>{apiInfo.message}</span>
                    </div>
                    <div style={styles.infoRow as React.CSSProperties}>
                      <span style={styles.infoLabel as React.CSSProperties}>Documentation</span>
                      <a
                        href={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/docs`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={styles.link as React.CSSProperties}
                      >
                        API Documentation
                      </a>
                    </div>
                  </>
                )}
              </div>

              {apiInfo && apiInfo.project_info && (
                <div style={styles.card as React.CSSProperties}>
                  <h2 style={styles.cardTitle as React.CSSProperties}>
                    <Icons.Project />
                    Project Information
                  </h2>
                  <div style={styles.infoRow as React.CSSProperties}>
                    <span style={styles.infoLabel as React.CSSProperties}>Name</span>
                    <span style={styles.infoValue as React.CSSProperties}>{apiInfo.project_info.name}</span>
                  </div>
                  <div style={styles.infoRow as React.CSSProperties}>
                    <span style={styles.infoLabel as React.CSSProperties}>Description</span>
                    <span style={styles.infoValue as React.CSSProperties}>{apiInfo.project_info.description}</span>
                  </div>
                  <div style={styles.infoRow as React.CSSProperties}>
                    <span style={styles.infoLabel as React.CSSProperties}>Environment</span>
                    <span style={{...styles.infoValue as React.CSSProperties, textTransform: 'capitalize'}}>
                      {apiInfo.project_info.environment}
                    </span>
                  </div>
                </div>
              )}

              <div style={styles.card as React.CSSProperties}>
                <h2 style={styles.cardTitle as React.CSSProperties}>
                  <Icons.Time />
                  Server Uptime
                </h2>
                <span style={styles.uptimeValue as React.CSSProperties}>
                  {formatUptime(uptime)}
                </span>
                <div style={{...styles.infoRow as React.CSSProperties, textAlign: 'center'}}>
                  <span style={styles.infoLabel as React.CSSProperties}>
                    Live updates via Server-Sent Events
                  </span>
                </div>
              </div>
            </div>
            
            <div style={styles.footer as React.CSSProperties}>
              © {new Date().getFullYear()} SwissHacks - Connecting Swiss Innovation
            </div>
          </>
        )}
      </div>
    </main>
  );
}