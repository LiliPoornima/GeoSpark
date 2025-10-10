// import React, { useState, useRef, useEffect } from 'react'
// import { apiEndpoints } from '../services/api'
// import toast from 'react-hot-toast'

// export function Agent() {
//   const [city, setCity] = useState('')
//   const [resourceType, setResourceType] = useState('solar')
//   const [message, setMessage] = useState('Analyze this city')
//   const [chatMode, setChatMode] = useState<'chat' | 'workflow'>('workflow')
//   const [history, setHistory] = useState<Array<{ role: 'user' | 'agent'; text: string }>>([])
//   const [results, setResults] = useState<any>(null)
//   const [isLoading, setIsLoading] = useState(false)

//   const chatRef = useRef<HTMLDivElement>(null)

//   // Auto-scroll chat to bottom on update
//   useEffect(() => {
//     if (chatRef.current) {
//       chatRef.current.scrollTop = chatRef.current.scrollHeight
//     }
//   }, [history])

//   const send = async () => {
//     if (!message.trim()) return

//     try {
//       setIsLoading(true)
//       setHistory(h => [...h, { role: 'user', text: message }])

//       const resp = await apiEndpoints.agentChat({
//         message,
//         city,
//         resource_type: resourceType,
//         mode: chatMode,
//       })

//       const data = resp.data

//       if (data.mode === 'workflow') {
//         setResults(data.results)
//         setHistory(h => [
//           ...h,
//           { role: 'agent', text: '✅ Completed site analysis, resource estimation, cost evaluation, and report.' },
//         ])
//       } else {
//         setHistory(h => [...h, { role: 'agent', text: data.message }])
//       }

//       setMessage('')
//     } catch (e: any) {
//       toast.error(e.response?.data?.error || 'Agent request failed')
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   return (
//     <div className="space-y-6">
//       <div>
//         <h1 className="text-2xl font-bold text-gray-900">⚡ AI Agent - Sparks</h1>
//         <p className="text-gray-600">Ask about site analysis, resources, costs, or reports.</p>
//       </div>

//       {/* Controls */}
//       <div className="flex items-end gap-3">
//         <div className="w-48">
//           <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
//           <input
//             className="w-full px-3 py-2 border rounded-md"
//             value={city}
//             onChange={e => setCity(e.target.value)}
//             placeholder="e.g., Kandy"
//           />
//         </div>
//         <div>
//           <label className="block text-sm font-medium text-gray-700 mb-1">Resource</label>
//           <select
//             className="px-3 py-2 border rounded-md"
//             value={resourceType}
//             onChange={e => setResourceType(e.target.value)}
//           >
//             <option value="solar">Solar</option>
//             <option value="wind">Wind</option>
//             <option value="hybrid">Hybrid</option>
//           </select>
//         </div>
//         <div>
//           <label className="block text-sm font-medium text-gray-700 mb-1">Mode</label>
//           <select
//             className="px-3 py-2 border rounded-md"
//             value={chatMode}
//             onChange={e => setChatMode(e.target.value as 'chat' | 'workflow')}
//           >
//             <option value="workflow">Workflow</option>
//             <option value="chat">Chat</option>
//           </select>
//         </div>
//         <div className="flex-1">
//           <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
//           <input
//             className="w-full px-3 py-2 border rounded-md"
//             value={message}
//             onChange={e => setMessage(e.target.value)}
//             onKeyDown={e => e.key === 'Enter' && !isLoading && send()}
//             placeholder="Ask the agent..."
//           />
//         </div>
//         <button
//           onClick={send}
//           disabled={isLoading}
//           className="bg-green-600 text-white px-4 py-2 rounded-md"
//         >
//           {isLoading ? '⚡ Thinking...' : 'Send'}
//         </button>
//       </div>

//       {/* Panels */}
//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
//         {/* Chat Panel */}
//         <div ref={chatRef} className="bg-white rounded-lg shadow p-4 h-96 overflow-auto">
//           <h3 className="font-semibold mb-2">Chat</h3>
//           <div className="space-y-2">
//             {history.map((m, i) => (
//               <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
//                 <span
//                   className={`inline-block px-3 py-2 rounded-md ${
//                     m.role === 'user'
//                       ? 'bg-green-600 text-white'
//                       : 'bg-gray-200 text-gray-800'
//                   }`}
//                 >
//                   {m.text}
//                 </span>
//               </div>
//             ))}
//           </div>
//         </div>

//         {/* Results Panel */}
//         <div className="bg-white rounded-lg shadow p-4">
//           <h3 className="font-semibold mb-2">Results</h3>
//           {!results ? (
//             <div className="text-gray-500">Ask to analyze a city to see results.</div>
//           ) : (
//             <div className="space-y-3 text-sm">
//               {Object.entries(results).map(([key, value]) => (
//                 <div key={key}>
//                   <div className="font-medium capitalize">{key.replace('_', ' ')}</div>
//                   <div className="bg-gray-50 p-2 rounded-md whitespace-pre-wrap">
//                     {JSON.stringify(value, null, 2)}
//                   </div>
//                 </div>
//               ))}
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   )
// }





// import React, { useState } from 'react'
// import { apiEndpoints } from '../services/api'
// import toast from 'react-hot-toast'

// export function Agent() {
//   const [city, setCity] = useState('')
//   const [resourceType, setResourceType] = useState('solar')
//   const [message, setMessage] = useState('Analyze this city')
//   const [chatMode, setChatMode] = useState<'chat'|'workflow'>('workflow')
//   const [history, setHistory] = useState<Array<{role: 'user'|'agent'; text: string}>>([])
//   const [results, setResults] = useState<any>(null)
//   const [isLoading, setIsLoading] = useState(false)

//   const send = async () => {
//     try {
//       setIsLoading(true)
//       setHistory(h => [...h, { role: 'user', text: message }])
//       const resp = await apiEndpoints.agentChat({ message, city, resource_type: resourceType, mode: chatMode })
//       const data = resp.data
//       if (data.mode === 'workflow') {
//         setResults(data.results)
//         setHistory(h => [...h, { role: 'agent', text: 'Completed site analysis, resource estimation, cost evaluation and report.' }])
//       } else {
//         setHistory(h => [...h, { role: 'agent', text: data.message }])
//       }
//     } catch (e) {
//       toast.error('Agent request failed')
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   return (
//     <div className="space-y-6">
//       <div>
//         <h1 className="text-2xl font-bold text-gray-900">AI Agent</h1>
//         <p className="text-gray-600">Ask about site analysis, resources, costs, or reports.</p>
//       </div>

//       <div className="flex items-end gap-3">
//         <div className="w-48">
//           <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
//           <input className="w-full px-3 py-2 border rounded-md" value={city} onChange={e=>setCity(e.target.value)} placeholder="e.g., Kandy" />
//         </div>
//         <div>
//           <label className="block text-sm font-medium text-gray-700 mb-1">Resource</label>
//           <select className="px-3 py-2 border rounded-md" value={resourceType} onChange={e=>setResourceType(e.target.value)}>
//             <option value="solar">Solar</option>
//             <option value="wind">Wind</option>
//             <option value="hybrid">Hybrid</option>
//           </select>
//         </div>
//         <div>
//           <label className="block text-sm font-medium text-gray-700 mb-1">Mode</label>
//           <select className="px-3 py-2 border rounded-md" value={chatMode} onChange={e=>setChatMode(e.target.value as 'chat'|'workflow')}>
//             <option value="workflow">Workflow</option>
//             <option value="chat">Chat</option>
//           </select>
//         </div>
//         <div className="flex-1">
//           <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
//           <input className="w-full px-3 py-2 border rounded-md" value={message} onChange={e=>setMessage(e.target.value)} placeholder="Ask the agent..." />
//         </div>
//         <button onClick={send} disabled={isLoading} className="bg-green-600 text-white px-4 py-2 rounded-md">{isLoading ? 'Thinking...' : 'Send'}</button>
//       </div>

//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
//         <div className="bg-white rounded-lg shadow p-4 h-96 overflow-auto">
//           <h3 className="font-semibold mb-2">Chat</h3>
//           <div className="space-y-2">
//             {history.map((m, i) => (
//               <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
//                 <span className={`inline-block px-3 py-2 rounded-md ${m.role === 'user' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-800'}`}>{m.text}</span>
//               </div>
//             ))}
//           </div>
//         </div>

//         <div className="bg-white rounded-lg shadow p-4">
//           <h3 className="font-semibold mb-2">Results</h3>
//           {!results ? (
//             <div className="text-gray-500">Ask to analyze a city to see results.</div>
//           ) : (
//             <div className="space-y-3 text-sm">
//               <div>
//                 <div className="font-medium">Site Analysis</div>
//                 <pre className="whitespace-pre-wrap">{JSON.stringify(results.site_analysis, null, 2)}</pre>
//               </div>
//               <div>
//                 <div className="font-medium">Resource Estimation</div>
//                 <pre className="whitespace-pre-wrap">{JSON.stringify(results.resource_estimation, null, 2)}</pre>
//               </div>
//               <div>
//                 <div className="font-medium">Cost Evaluation</div>
//                 <pre className="whitespace-pre-wrap">{JSON.stringify(results.cost_evaluation, null, 2)}</pre>
//               </div>
//               <div>
//                 <div className="font-medium">Report Summary</div>
//                 <pre className="whitespace-pre-wrap">{JSON.stringify(results.report, null, 2)}</pre>
//               </div>
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   )
// }


