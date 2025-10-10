import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Zap, Search, CornerDownLeft } from 'lucide-react';
import solar from '../assets/solar.jpg';
import wind from '../assets/wind.jpg';
import hydro from '../assets/hydro.jpg';

// === Type Definitions ===
interface Source {
    uri: string;
    title: string;
}

interface Message {
    id: string;
    role: 'user' | 'model' | 'system';
    text: string;
    sources?: Source[];
    isLoading?: boolean;
}

// === Constants ===
const MODEL_NAME = "gemini-2.5-flash-preview-05-20";
const API_URL_BASE = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent`;

// Placeholder images for the background slideshow (Local imports removed and replaced with URLs)
const BACKGROUND_IMAGES = [
    solar,
    wind,
    hydro
];

// Retrieve API key from global scope (assumed to be provided by the environment)
// NOTE: API Key must be an empty string for the platform to inject it.
const apiKey = "AIzaSyDWJHKjQs304ZJx89YB28BXeDV0sfiXzOo"; 

// The system instruction defining the "Sparks" persona, translated from the Python code.
const systemPrompt = `You are an expert in renewable energy. Your name is Sparks. You are the chatbot for a renewable energy site selector system with 3 features: location analysis, resource estimation, and cost evaluation. You can use Google Search to fetch real-time information about renewable energy. Engage interactively with users, explain concepts clearly, use interesting greetings, and share fun facts about renewable energy when it is appropriate. ALWAYS structure long answers or lists using clear, easy-to-read Markdown formatting, such as **numbered lists** or **bolded section headings**, to improve clarity and readability, avoiding excessive use of asterisks for list items.`;

// === Utility Functions ===

/**
 * Handles the fetch call with exponential backoff for resilience.
 */
async function fetchWithExponentialBackoff(
    url: string,
    options: RequestInit,
    maxRetries: number = 3
): Promise<Response> {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const response = await fetch(url, options);
            if (response.ok) {
                return response;
            }
            // If response is not OK, we might retry based on status code
            if (response.status === 429 || response.status >= 500) {
                if (attempt === maxRetries - 1) throw new Error(`API failed after ${maxRetries} attempts with status: ${response.status}`);
            } else {
                // For non-retriable errors (like 400s), break and throw
                throw new Error(`API failed with status: ${response.status}`);
            }
        } catch (error) {
            if (attempt === maxRetries - 1) throw error;
        }

        const delay = Math.pow(2, attempt) * 1000 + Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
    }
    throw new Error("Exceeded max retries");
}

/**
 * Parses the response from the Gemini API and extracts text and grounding sources.
 */
function parseGeminiResponse(result: any): { text: string; sources: Source[] } {
    const candidate = result.candidates?.[0];
    let text = candidate?.content?.parts?.[0]?.text || "I'm sorry, I couldn't generate a response.";
    let sources: Source[] = [];

    const groundingMetadata = candidate?.groundingMetadata;
    if (groundingMetadata && groundingMetadata.groundingAttributions) {
        sources = groundingMetadata.groundingAttributions
            .map((attribution: any) => ({
                uri: attribution.web?.uri,
                title: attribution.web?.title,
            }))
            .filter((source: Source) => source.uri && source.title) as Source[];
    }

    return { text, sources };
}

// === Components ===

/**
 * Renders a single chat bubble (User or Model).
 */
const ChatBubble: React.FC<{ message: Message }> = ({ message }) => {
    const isUser = message.role === 'user';
    
    // --- Consistency Changes Applied ---
    const bgColor = isUser ? 'bg-green-600' : 'bg-gray-200';
    const textColor = isUser ? 'text-white' : 'text-gray-900';
    // -----------------------------------

    const alignment = isUser ? 'justify-end' : 'justify-start';

    return (
        <div className={`flex w-full mb-4 ${alignment}`}>
            <div className={`max-w-3xl p-4 rounded-xl shadow-lg ${bgColor} ${textColor} ${isUser ? 'rounded-br-none' : 'rounded-tl-none'}`}>
                {message.isLoading ? (
                    <div className="flex items-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {/* Adjusted text color for light model bubble */}
                        <span className={isUser ? 'text-white' : 'text-gray-700'}>Sparks is thinking...</span>
                    </div>
                ) : (
                    <>
                        <p className="whitespace-pre-wrap">{message.text}</p>
                        {message.sources && message.sources.length > 0 && (
                            <div className={`mt-3 pt-2 border-t text-xs opacity-80 ${isUser ? 'border-green-400/50 text-green-100' : 'border-gray-400/50 text-green-700'}`}>
                                <p className={`flex items-center mb-1 font-semibold ${isUser ? 'text-white' : 'text-green-700'}`}>
                                    <Search className="w-3 h-3 mr-1" />
                                    Sources
                                </p>
                                <ul className="list-disc list-inside space-y-1">
                                    {message.sources.slice(0, 3).map((source, index) => (
                                        <li key={index} className="truncate hover:text-green-800">
                                            <a href={source.uri} target="_blank" rel="noopener noreferrer" className="underline">
                                                {source.title || source.uri}
                                            </a>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

/**
 * Main Sparks Chatbot component.
 */
const SparksChatbot: React.FC = () => {
    
    const [messages, setMessages] = useState<Message[]>([
        { 
            id: 'initial', 
            role: 'model', 
            text: `⚡ Greetings! I'm Sparks, your expert in renewable energy. I'm here to help you navigate location analysis, resource estimation, and cost evaluation for your renewable energy site selector system. What brilliant question do you have for me today?`, 
            sources: [] 
        }
    ]);
    const [input, setInput] = useState('');
    const [isSending, setIsSending] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    // Scroll to the latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    //Slideshow background logic
    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentImageIndex(prevIndex => 
                (prevIndex + 1) % BACKGROUND_IMAGES.length
            );
        }, 8000); // Change image every 8 seconds

        return () => clearInterval(interval);
    }, []);

    /**
     * Handles sending the message to the Gemini API.
     */
    const handleSend = async () => {
        const messageText = input.trim();
        if (!messageText || isSending) return;

        setIsSending(true);
        setInput('');

        // Define IDs for the new messages up front
        const newUserMessageId = crypto.randomUUID();
        const loadingMessageId = crypto.randomUUID();

        // 1. Prepare chat history for the API call (use the current `messages` state snapshot)
        // Ensure we only use non-system, non-loading messages for the contents history.
        const chatHistory = messages
            .filter(m => !m.isLoading && m.role !== 'system')
            .map(m => ({
                role: m.role,
                parts: [{ text: m.text }],
            }));
        
        // 2. Add current user message to the contents payload
        const contents = [...chatHistory, { role: 'user', parts: [{ text: messageText }] }];

        // 3. Update UI state with the new user message and the temporary loading message
        // This is done *before* the fetch to provide immediate UI feedback.
        setMessages(prev => [
            ...prev, 
            { id: newUserMessageId, role: 'user', text: messageText },
            { id: loadingMessageId, role: 'model', text: '', isLoading: true }
        ]);
        
        // 4. Construct API payload 
        const payload = {
            contents: contents, // Use the correctly formatted history + new query
            tools: [{ "google_search": {} }], 
            systemInstruction: {
                parts: [{ text: systemPrompt }]
            },
        };

        const apiUrl = `${API_URL_BASE}?key=${apiKey}`;

        try {
            const response = await fetchWithExponentialBackoff(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            const { text: modelResponseText, sources } = parseGeminiResponse(result);

            // 5. Update state with the final model response
            setMessages(prev => {
                // Find and replace the loading message using the known ID
                return prev.map(m => 
                    m.id === loadingMessageId ? { 
                        ...m, 
                        text: modelResponseText, 
                        sources: sources, 
                        isLoading: false 
                    } : m
                );
            });

        } catch (error) {
            // New logic: Extract specific error message for better visibility
            const errorMessage = error instanceof Error ? error.message : "An unknown API error occurred.";
            console.error("Gemini API Error:", errorMessage);
            
            // 6. Replace loading message with a detailed error message
            setMessages(prev => {
                // Find and replace the loading message using the known ID
                return prev.map(m => 
                    m.id === loadingMessageId ? { 
                        ...m, 
                        // Provide the captured error message to the user
                        text: `Oops! I encountered an error. The request failed: ${errorMessage}. Please try again or rephrase your question.`, 
                        isLoading: false 
                    } : m
                );
            });
        } finally {
            setIsSending(false);
        }
    };

    /**
     * Allows sending message via Enter key.
     */
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !isSending && input.trim()) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        // New full-screen container for the background and chat content (1. Outermost div)
        <div className="relative h-screen w-full font-inter overflow-hidden">
            {/* === Background Slideshow Layer (z-0) === */}
            <div className="absolute inset-0">
                {BACKGROUND_IMAGES.map((url, index) => (
                    <img
                        key={index}
                        src={url}
                        alt="Renewable Energy Background"
                        className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ease-in-out`}
                        style={{
                            // Only show the active image, with low opacity for subtlety
                            opacity: index === currentImageIndex ? 0.7 : 0, 
                        }}
                        onError={(e) => { e.currentTarget.onerror = null; e.currentTarget.src = "https://placehold.co/1200x800/1e293b/ffffff?text=Energy"; }}
                    />
                ))}
            </div>
            
            {/* === Chat Interface Layer (z-10) === */}
            {/* This container centers the chatbot on the screen and provides padding */}
            <div className="relative z-10 flex flex-col h-full max-w-4xl mx-auto p-4 sm:p-8"> 
                <div className="flex flex-col h-full w-full bg-white/95 backdrop-blur-sm text-gray-900 rounded-xl shadow-2xl overflow-hidden border border-gray-200">
                    
                    {/* Header - Changed colors to use green branding */}
                    <div className="p-4 bg-green-600 border-b border-green-800 flex items-center shadow-md text-white">
                        <Zap className="h-6 w-6 text-white mr-3" />
                        <h1 className="text-xl font-bold">Sparks Chatbot</h1>
                        {/* Changed badge color */}
                        <span className="ml-3 px-2 py-1 text-xs bg-green-900/50 rounded-full">Renewable Energy AI</span>
                    </div>

                    {/* Message Display Area - Added transparency to the background */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/70 custom-scrollbar"> 
                        {messages.map((message) => (
                            <ChatBubble key={message.id} message={message} />
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area - Added transparency to the background */}
                    <div className="p-4 bg-white/95 border-t border-gray-200">
                        <div className="relative flex items-center">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask Sparks about location, resource, or cost evaluation..."
                                disabled={isSending}
                                // Changed input field styling for light theme
                                className="w-full p-3 pr-12 text-sm bg-white text-gray-800 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 transition duration-150 placeholder-gray-500"
                            />
                            <button
                                onClick={handleSend}
                                disabled={isSending || !input.trim()}
                                className={`absolute right-0 mr-1 p-2 rounded-lg transition duration-150 ${
                                    // Changed button colors to use green branding
                                    isSending || !input.trim()
                                        ? 'bg-green-700/50 text-gray-400 cursor-not-allowed'
                                        : 'bg-green-600 hover:bg-green-500 text-white shadow-lg transform hover:scale-105'
                                }`}
                                title="Send Message"
                            >
                                {isSending ? (
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                ) : (
                                    <Send className="h-5 w-5" />
                                )}
                            </button>
                        </div>
                        {/* Changed hint text color */}
                        <p className="text-xs text-gray-600 mt-2 flex items-center">
                            <CornerDownLeft className="w-3 h-3 mr-1" />
                            Press Enter to send. Powered by Gemini with Google Search grounding.
                        </p>
                    </div>

                    {/* Custom Scrollbar Styling (FIX: Removed jsx="true" attribute) */}
                    <style>{`
                        .custom-scrollbar::-webkit-scrollbar {
                            width: 8px;
                        }
                        .custom-scrollbar::-webkit-scrollbar-track {
                            background: #f9fafb; /* bg-gray-50 */
                        }
                        .custom-scrollbar::-webkit-scrollbar-thumb {
                            background: #059669; /* bg-green-600 */
                            border-radius: 4px;
                        }
                        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                            background: #10b981; /* bg-green-500 */
                        }
                    `}</style>
                </div>
            </div>
        </div>
    );
};

// Required default export for the React file structure
export default SparksChatbot;


// import React, { useState, useRef, useEffect } from 'react';
// import { Send, Loader2, Zap, Search, CornerDownLeft } from 'lucide-react';
// import solar from '../assets/solar.jpg';
// import wind from '../assets/wind.jpg';
// import hydro from '../assets/hydro.jpg';

// // === Type Definitions ===
// interface Source {
//     uri: string;
//     title: string;
// }

// interface Message {
//     id: string;
//     role: 'user' | 'model' | 'system';
//     text: string;
//     sources?: Source[];
//     isLoading?: boolean;
// }

// // === Constants ===
// const MODEL_NAME = "gemini-2.5-flash-preview-05-20";
// const API_URL_BASE = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent`;

// // Placeholder images for the background slideshow
// const BACKGROUND_IMAGES = [
//     solar, // Forest Green/White
//     wind, // Gold/Black   // Dodger Blue/White
//     hydro // Blue Violet/White
// ];

// // Retrieve API key from global scope (assumed to be provided by the environment)
// // NOTE: For this environment, the key must be an empty string for the platform to inject it.
// const apiKey = "AIzaSyDWJHKjQs304ZJx89YB28BXeDV0sfiXzOo"; 

// // The system instruction defining the "Sparks" persona, translated from the Python code.
// const systemPrompt = `You are an expert in renewable energy. Your name is Sparks. You are the chatbot for a renewable energy site selector system with 3 features: location analysis, resource estimation, and cost evaluation. You can use Google Search to fetch real-time information about renewable energy. Engage interactively with users, explain concepts clearly, use interesting greetings, and share fun facts about renewable energy when it is appropriate. ALWAYS structure long answers or lists using clear, easy-to-read Markdown formatting, such as **numbered lists** or **bolded section headings**, to improve clarity and readability, avoiding excessive use of asterisks for list items.`;

// // === Utility Functions ===

// /**
//  * Handles the fetch call with exponential backoff for resilience.
//  */
// async function fetchWithExponentialBackoff(
//     url: string,
//     options: RequestInit,
//     maxRetries: number = 3
// ): Promise<Response> {
//     for (let attempt = 0; attempt < maxRetries; attempt++) {
//         try {
//             const response = await fetch(url, options);
//             if (response.ok) {
//                 return response;
//             }
//             // If response is not OK, we might retry based on status code
//             if (response.status === 429 || response.status >= 500) {
//                 if (attempt === maxRetries - 1) throw new Error(`API failed after ${maxRetries} attempts with status: ${response.status}`);
//             } else {
//                 // For non-retriable errors (like 400s), break and throw
//                 throw new Error(`API failed with status: ${response.status}`);
//             }
//         } catch (error) {
//             if (attempt === maxRetries - 1) throw error;
//         }

//         const delay = Math.pow(2, attempt) * 1000 + Math.random() * 1000;
//         await new Promise(resolve => setTimeout(resolve, delay));
//     }
//     throw new Error("Exceeded max retries");
// }

// /**
//  * Parses the response from the Gemini API and extracts text and grounding sources.
//  */
// function parseGeminiResponse(result: any): { text: string; sources: Source[] } {
//     const candidate = result.candidates?.[0];
//     let text = candidate?.content?.parts?.[0]?.text || "I'm sorry, I couldn't generate a response.";
//     let sources: Source[] = [];

//     const groundingMetadata = candidate?.groundingMetadata;
//     if (groundingMetadata && groundingMetadata.groundingAttributions) {
//         sources = groundingMetadata.groundingAttributions
//             .map((attribution: any) => ({
//                 uri: attribution.web?.uri,
//                 title: attribution.web?.title,
//             }))
//             .filter((source: Source) => source.uri && source.title) as Source[];
//     }

//     return { text, sources };
// }

// // === Components ===

// /**
//  * Renders a single chat bubble (User or Model).
//  */
// const ChatBubble: React.FC<{ message: Message }> = ({ message }) => {
//     const isUser = message.role === 'user';
    
//     // --- Consistency Changes Applied ---
//     const bgColor = isUser ? 'bg-green-600' : 'bg-gray-200';
//     const textColor = isUser ? 'text-white' : 'text-gray-900';
//     // -----------------------------------

//     const alignment = isUser ? 'justify-end' : 'justify-start';

//     return (
//         <div className={`flex w-full mb-4 ${alignment}`}>
//             <div className={`max-w-3xl p-4 rounded-xl shadow-lg ${bgColor} ${textColor} ${isUser ? 'rounded-br-none' : 'rounded-tl-none'}`}>
//                 {message.isLoading ? (
//                     <div className="flex items-center space-x-2">
//                         <Loader2 className="h-4 w-4 animate-spin" />
//                         {/* Adjusted text color for light model bubble */}
//                         <span className={isUser ? 'text-white' : 'text-gray-700'}>Sparks is thinking...</span>
//                     </div>
//                 ) : (
//                     <>
//                         <p className="whitespace-pre-wrap">{message.text}</p>
//                         {message.sources && message.sources.length > 0 && (
//                             <div className={`mt-3 pt-2 border-t text-xs opacity-80 ${isUser ? 'border-green-400/50 text-green-100' : 'border-gray-400/50 text-green-700'}`}>
//                                 <p className={`flex items-center mb-1 font-semibold ${isUser ? 'text-white' : 'text-green-700'}`}>
//                                     <Search className="w-3 h-3 mr-1" />
//                                     Sources
//                                 </p>
//                                 <ul className="list-disc list-inside space-y-1">
//                                     {message.sources.slice(0, 3).map((source, index) => (
//                                         <li key={index} className="truncate hover:text-green-800">
//                                             <a href={source.uri} target="_blank" rel="noopener noreferrer" className="underline">
//                                                 {source.title || source.uri}
//                                             </a>
//                                         </li>
//                                     ))}
//                                 </ul>
//                             </div>
//                         )}
//                     </>
//                 )}
//             </div>
//         </div>
//     );
// };

// /**
//  * Main Sparks Chatbot component.
//  */
// const SparksChatbot: React.FC = () => {
    
//     const [messages, setMessages] = useState<Message[]>([
//         { 
//             id: 'initial', 
//             role: 'model', 
//             text: `⚡ Greetings! I'm Sparks, your expert in renewable energy. I'm here to help you navigate location analysis, resource estimation, and cost evaluation for your renewable energy site selector system. What brilliant question do you have for me today?`, 
//             sources: [] 
//         }
//     ]);
//     const [input, setInput] = useState('');
//     const [isSending, setIsSending] = useState(false);
//     const messagesEndRef = useRef<HTMLDivElement>(null);
//     const [currentImageIndex, setCurrentImageIndex] = useState(0);

//     // Scroll to the latest message
//     useEffect(() => {
//         messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//     }, [messages]);

//     //Slideshow background logic
//     useEffect(() => {
//         const interval = setInterval(() => {
//             setCurrentImageIndex(prevIndex => 
//                 (prevIndex + 1) % BACKGROUND_IMAGES.length
//             );
//         }, 8000); // Change image every 8 seconds

//         return () => clearInterval(interval);
//     }, []);

//     /**
//      * Handles sending the message to the Gemini API.
//      */
//     const handleSend = async () => {
//         const messageText = input.trim();
//         if (!messageText || isSending) return;

//         setIsSending(true);
//         setInput('');

//         // Define IDs for the new messages up front
//         const newUserMessageId = crypto.randomUUID();
//         const loadingMessageId = crypto.randomUUID();

//         // 1. Prepare chat history for the API call (use the current `messages` state snapshot)
//         // Ensure we only use non-system, non-loading messages for the contents history.
//         const chatHistory = messages
//             .filter(m => !m.isLoading && m.role !== 'system')
//             .map(m => ({
//                 role: m.role,
//                 parts: [{ text: m.text }],
//             }));
        
//         // 2. Add current user message to the contents payload
//         const contents = [...chatHistory, { role: 'user', parts: [{ text: messageText }] }];

//         // 3. Update UI state with the new user message and the temporary loading message
//         // This is done *before* the fetch to provide immediate UI feedback.
//         setMessages(prev => [
//             ...prev, 
//             { id: newUserMessageId, role: 'user', text: messageText },
//             { id: loadingMessageId, role: 'model', text: '', isLoading: true }
//         ]);
        
//         // 4. Construct API payload (RE-ADDED 'tools' BLOCK)
//         const payload = {
//             contents: contents, // Use the correctly formatted history + new query
//             tools: [{ "google_search": {} }], // RE-ADDED to ensure policy requirements are met
//             systemInstruction: {
//                 parts: [{ text: systemPrompt }]
//             },
//         };

//         const apiUrl = `${API_URL_BASE}?key=${apiKey}`;

//         try {
//             const response = await fetchWithExponentialBackoff(apiUrl, {
//                 method: 'POST',
//                 headers: { 'Content-Type': 'application/json' },
//                 body: JSON.stringify(payload)
//             });

//             const result = await response.json();
//             const { text: modelResponseText, sources } = parseGeminiResponse(result);

//             // 5. Update state with the final model response
//             setMessages(prev => {
//                 // Find and replace the loading message using the known ID
//                 return prev.map(m => 
//                     m.id === loadingMessageId ? { 
//                         ...m, 
//                         text: modelResponseText, 
//                         sources: sources, 
//                         isLoading: false 
//                     } : m
//                 );
//             });

//         } catch (error) {
//             // New logic: Extract specific error message for better visibility
//             const errorMessage = error instanceof Error ? error.message : "An unknown API error occurred.";
//             console.error("Gemini API Error:", errorMessage);
            
//             // 6. Replace loading message with a detailed error message
//             setMessages(prev => {
//                 // Find and replace the loading message using the known ID
//                 return prev.map(m => 
//                     m.id === loadingMessageId ? { 
//                         ...m, 
//                         // Provide the captured error message to the user
//                         text: `Oops! I encountered an error. The request failed: ${errorMessage}. Please try again or rephrase your question.`, 
//                         isLoading: false 
//                     } : m
//                 );
//             });
//         } finally {
//             setIsSending(false);
//         }
//     };

//     /**
//      * Allows sending message via Enter key.
//      */
//     const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
//         if (e.key === 'Enter' && !isSending && input.trim()) {
//             e.preventDefault();
//             handleSend();
//         }
//     };

//     return (
        
//         // New full-screen container for the background and chat content
//         <div className="relative h-screen w-full font-inter overflow-hidden">
//             {/* === Background Slideshow Layer (z-0) === */}
//             <div className="absolute inset-0">
//                 {BACKGROUND_IMAGES.map((url, index) => (
//                     <img
//                         key={index}
//                         src={url}
//                         alt="Renewable Energy Background"
//                         className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ease-in-out`}
//                         style={{
//                             // Only show the active image, with low opacity for subtlety
//                             opacity: index === currentImageIndex ? 0.2 : 0, 
//                         }}
//                         onError={(e) => { e.currentTarget.onerror = null; e.currentTarget.src = "https://placehold.co/1200x800/1e293b/ffffff?text=Energy"; }}
//                     />
//                 ))}
//         </div>
        

//         // Changed main container background and text color to fit light theme
//         <div className="flex flex-col h-full bg-white text-gray-900 font-inter rounded-xl shadow-2xl overflow-hidden max-w-4xl mx-auto border border-gray-200">
//             {/* Header - Changed colors to use green branding */}
//             <div className="p-4 bg-green-600 border-b border-green-800 flex items-center shadow-md text-white">
//                 <Zap className="h-6 w-6 text-white mr-3" />
//                 <h1 className="text-xl font-bold">Sparks Chatbot</h1>
//                 {/* Changed badge color */}
//                 <span className="ml-3 px-2 py-1 text-xs bg-green-900/50 rounded-full">Renewable Energy AI</span>
//             </div>

//             {/* Message Display Area - Changed background to a light gray for better contrast with white input/bubbles */}
//             <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 custom-scrollbar">
//                 {messages.map((message) => (
//                     <ChatBubble key={message.id} message={message} />
//                 ))}
//                 <div ref={messagesEndRef} />
//             </div>

//             {/* Input Area - Changed background and border to match light theme */}
//             <div className="p-4 bg-white border-t border-gray-200">
//                 <div className="relative flex items-center">
//                     <input
//                         type="text"
//                         value={input}
//                         onChange={(e) => setInput(e.target.value)}
//                         onKeyDown={handleKeyDown}
//                         placeholder="Ask Sparks about location, resource, or cost evaluation..."
//                         disabled={isSending}
//                         // Changed input field styling for light theme
//                         className="w-full p-3 pr-12 text-sm bg-white text-gray-800 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 transition duration-150 placeholder-gray-500"
//                     />
//                     <button
//                         onClick={handleSend}
//                         disabled={isSending || !input.trim()}
//                         className={`absolute right-0 mr-1 p-2 rounded-lg transition duration-150 ${
//                             // Changed button colors to use green branding
//                             isSending || !input.trim()
//                                 ? 'bg-green-700/50 text-gray-400 cursor-not-allowed'
//                                 : 'bg-green-600 hover:bg-green-500 text-white shadow-lg transform hover:scale-105'
//                         }`}
//                         title="Send Message"
//                     >
//                         {isSending ? (
//                             <Loader2 className="h-5 w-5 animate-spin" />
//                         ) : (
//                             <Send className="h-5 w-5" />
//                         )}
//                     </button>
//                 </div>
//                 {/* Changed hint text color */}
//                 <p className="text-xs text-gray-600 mt-2 flex items-center">
//                     <CornerDownLeft className="w-3 h-3 mr-1" />
//                     Press Enter to send. Powered by Gemini with Google Search grounding.
//                 </p>
//             </div>

//             {/* Custom Scrollbar Styling (FIX: Removed jsx="true" attribute) */}
//             <style>{`
//                 .custom-scrollbar::-webkit-scrollbar {
//                     width: 8px;
//                 }
//                 .custom-scrollbar::-webkit-scrollbar-track {
//                     background: #f9fafb; /* bg-gray-50 */
//                 }
//                 .custom-scrollbar::-webkit-scrollbar-thumb {
//                     background: #059669; /* bg-green-600 */
//                     border-radius: 4px;
//                 }
//                 .custom-scrollbar::-webkit-scrollbar-thumb:hover {
//                     background: #10b981; /* bg-green-500 */
//                 }
//             `}</style>
//         </div>
//     );
// };

// // Required default export for the React file structure
// export default SparksChatbot;


