"use client";

import { useState } from "react";

interface Port {
  port: string;
  state: string;
  service: string;
  version: string;
}

interface ScanResult {
  target: string;
  open_ports: Port[];
  cves: string[];
}

interface ScanError {
  message: string;
}

export default function Home() {
  const [target, setTarget] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    if (!target.trim()) {
      setError("Please enter a target (domain or IP address)");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/scan?target=${encodeURIComponent(target.trim())}`
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Scan failed" }));
        throw new Error(errorData.detail || `HTTP ${response.status}: Scan failed`);
      }

      const data: ScanResult = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Scan error:", err);
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !loading) {
      handleScan();
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 text-blue-400">
            Vulnerability Scanner
          </h1>
          <p className="text-gray-300 text-lg">
            Automated network security scanning with Nmap
          </p>
        </header>

        {/* Scan Input */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter domain or IP address (e.g., scanme.nmap.org)"
              className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              onClick={handleScan}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
            >
              {loading ? "Scanning..." : "Start Scan"}
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-gray-800 rounded-lg p-6 mb-8">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
              <span className="ml-3 text-gray-300">
                Running security scan... This may take up to 2 minutes
              </span>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-900 border border-red-700 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-red-400 mb-2">Scan Failed</h3>
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-8">
            {/* Summary */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4 text-green-400">
                Scan Results for {result.target}
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-gray-700 rounded p-4">
                  <h3 className="text-lg font-semibold text-blue-400">Open Ports</h3>
                  <p className="text-3xl font-bold text-white">
                    {result.open_ports.length}
                  </p>
                </div>
                <div className="bg-gray-700 rounded p-4">
                  <h3 className="text-lg font-semibold text-red-400">CVE Vulnerabilities</h3>
                  <p className="text-3xl font-bold text-white">
                    {result.cves.length}
                  </p>
                </div>
              </div>
            </div>

            {/* Open Ports Table */}
            {result.open_ports.length > 0 && (
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 text-blue-400">Open Ports</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Port
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          State
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Service
                        </th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-300">
                          Version
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.open_ports.map((port, index) => (
                        <tr key={index} className="border-b border-gray-700 hover:bg-gray-700">
                          <td className="py-3 px-4 font-mono text-blue-300">
                            {port.port}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${
                              port.state === "open" 
                                ? "bg-green-900 text-green-300" 
                                : "bg-gray-700 text-gray-300"
                            }`}>
                              {port.state}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-300">{port.service}</td>
                          <td className="py-3 px-4 text-gray-400 text-xs">
                            {port.version}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* CVE List */}
            {result.cves.length > 0 && (
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 text-red-400">
                  CVE Vulnerabilities
                </h3>
                <div className="space-y-2">
                  {result.cves.map((cve, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-700 rounded p-3">
                      <span className="font-mono text-red-300">{cve}</span>
                      <a
                        href={`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${cve}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 text-sm font-medium"
                      >
                        View Details →
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Results */}
            {result.open_ports.length === 0 && result.cves.length === 0 && (
              <div className="bg-gray-800 rounded-lg p-6 text-center">
                <p className="text-gray-400">
                  No open ports or vulnerabilities detected.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
