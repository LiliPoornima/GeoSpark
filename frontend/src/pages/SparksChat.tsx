import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Zap, Search, CornerDownLeft, Trash2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import solar from '../assets/solar.jpg';
import wind from '../assets/wind.jpg';
import hydro from '../assets/hydro.jpg';
import StripePaymentModal from '../components/StripePaymentModal';
import { useAuth } from '../contexts/AuthContext';

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

    return (
        <div className={`flex w-full mb-8 animate-fadeIn ${isUser ? 'justify-end' : 'justify-start'}`}>
            {/* Bot Avatar */}
            {!isUser && (
                <div className="flex-shrink-0 mr-4">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-sm">
                        <Zap className="w-4 h-4 text-white" />
                    </div>
                </div>
            )}
            
            <div className={`flex-1 ${isUser ? 'max-w-3xl ml-auto' : 'max-w-3xl'}`}>
                {/* Message Content */}
                <div className={`${isUser ? 'bg-gradient-to-br from-green-500 to-emerald-600 text-white' : 'bg-white text-gray-900'} rounded-2xl px-5 py-4 shadow-sm border ${isUser ? 'border-transparent' : 'border-gray-200'}`}>
                    {message.isLoading ? (
                        <div className="flex items-center space-x-3 py-2">
                            <div className="flex space-x-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                            </div>
                            <span className="text-sm text-gray-600">Thinking...</span>
                        </div>
                    ) : (
                        <>
                            <div className="text-[15px] leading-relaxed">
                                <MarkdownMessage content={message.text} isUser={isUser} />
                            </div>
                            {message.sources && message.sources.length > 0 && (
                                <div className={`mt-4 pt-4 border-t ${isUser ? 'border-green-400/30' : 'border-gray-200'}`}>
                                    <p className={`flex items-center mb-2 text-xs font-semibold uppercase tracking-wider ${isUser ? 'text-green-100' : 'text-gray-600'}`}>
                                        <Search className="w-3.5 h-3.5 mr-1.5" />
                                        Sources
                                    </p>
                                    <div className="space-y-2">
                                        {message.sources.slice(0, 3).map((source, index) => (
                                            <a 
                                                key={index} 
                                                href={source.uri} 
                                                target="_blank" 
                                                rel="noopener noreferrer" 
                                                className={`flex items-start text-xs hover:underline transition-colors ${
                                                    isUser ? 'text-green-50 hover:text-white' : 'text-green-600 hover:text-green-800'
                                                }`}
                                            >
                                                <span className="mr-2 mt-0.5">•</span>
                                                <span className="flex-1">{source.title || source.uri}</span>
                                            </a>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>

            {/* User Avatar */}
            {isUser && (
                <div className="flex-shrink-0 ml-4">
                    <div className="w-8 h-8 rounded-lg bg-gray-700 flex items-center justify-center shadow-sm text-white font-medium text-xs">
                        U
                    </div>
                </div>
            )}
        </div>
    );
};

/**
 * Markdown Message Component with custom styling
 */
const MarkdownMessage: React.FC<{ content: string; isUser: boolean }> = ({ content, isUser }) => {
    return (
        <div className={`prose prose-sm max-w-none ${isUser ? 'prose-invert' : ''}`}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    h1: ({node, ...props}) => <h1 className="text-xl font-bold mb-3 mt-4" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-lg font-bold mb-2 mt-3" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-base font-semibold mb-2 mt-2" {...props} />,
                    h4: ({node, ...props}) => <h4 className="text-sm font-semibold mb-1 mt-2" {...props} />,
                    p: ({node, ...props}) => <p className="mb-2 leading-relaxed" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-2 space-y-1" {...props} />,
                    li: ({node, ...props}) => <li className="ml-2" {...props} />,
                    strong: ({node, ...props}) => <strong className="font-bold" {...props} />,
                    em: ({node, ...props}) => <em className="italic" {...props} />,
                    code: ({node, inline, ...props}: any) => 
                        inline ? (
                            <code className={`px-1.5 py-0.5 rounded text-xs font-mono ${isUser ? 'bg-green-700' : 'bg-gray-200'}`} {...props} />
                        ) : (
                            <code className={`block p-3 rounded-lg text-xs font-mono my-2 ${isUser ? 'bg-green-700' : 'bg-gray-100'}`} {...props} />
                        ),
                    blockquote: ({node, ...props}) => <blockquote className={`border-l-4 pl-3 my-2 italic ${isUser ? 'border-green-300' : 'border-green-500'}`} {...props} />,
                    a: ({node, ...props}) => <a className="underline hover:no-underline" target="_blank" rel="noopener noreferrer" {...props} />,
                    table: ({node, ...props}) => <div className="overflow-x-auto my-2"><table className="min-w-full border-collapse" {...props} /></div>,
                    th: ({node, ...props}) => <th className={`border px-2 py-1 text-left font-semibold ${isUser ? 'border-green-400 bg-green-700' : 'border-gray-300 bg-gray-100'}`} {...props} />,
                    td: ({node, ...props}) => <td className={`border px-2 py-1 ${isUser ? 'border-green-400' : 'border-gray-300'}`} {...props} />,
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
};

/**
 * Main Sparks Chatbot component.
 */
const SparksChatbot: React.FC = () => {
    // Get auth context to detect user changes
    const { user } = useAuth();
    
    // Store the current user ID to detect changes
    const [currentUserId, setCurrentUserId] = useState<string | null>(
        localStorage.getItem('sparks_current_user_id')
    );
    
    // Load initial messages from localStorage or use default
    const getInitialMessages = (): Message[] => {
        try {
            const savedMessages = localStorage.getItem('sparks_chat_messages');
            if (savedMessages) {
                return JSON.parse(savedMessages);
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
        return [
            { 
                id: 'initial', 
                role: 'model', 
                text: `⚡ Greetings! I'm Sparks, your expert in renewable energy. I'm here to help you navigate location analysis, resource estimation, and cost evaluation for your renewable energy site selector system. What brilliant question do you have for me today?`, 
                sources: [] 
            }
        ];
    };

    // Load initial state from localStorage
    const getInitialMessageCount = (): number => {
        try {
            const savedCount = localStorage.getItem('sparks_message_count');
            return savedCount ? parseInt(savedCount, 10) : 0;
        } catch (error) {
            return 0;
        }
    };

    const getInitialAccess = (): boolean => {
        try {
            const savedAccess = localStorage.getItem('sparks_has_access');
            const savedPremiumUserId = localStorage.getItem('sparks_premium_user_id');
            const storedCurrentUserId = localStorage.getItem('sparks_current_user_id');
            
            // Only grant access if:
            // 1. Access is marked as true
            // 2. The premium access belongs to the current user
            if (savedAccess === 'true' && savedPremiumUserId && savedPremiumUserId === storedCurrentUserId) {
                return true;
            }
            
            // If there's a mismatch, clear the invalid premium access
            if (savedAccess === 'true' && savedPremiumUserId !== storedCurrentUserId) {
                localStorage.removeItem('sparks_has_access');
                localStorage.removeItem('sparks_premium_user_id');
            }
            
            return false;
        } catch (error) {
            return false;
        }
    };

    const [messages, setMessages] = useState<Message[]>(getInitialMessages);
    const [input, setInput] = useState('');
    const [isSending, setIsSending] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const [hasAccess, setHasAccess] = useState(getInitialAccess);
    const [showPaymentModal, setShowPaymentModal] = useState(false);
    const [messageCount, setMessageCount] = useState(getInitialMessageCount);
    const FREE_MESSAGE_LIMIT = 3;

    // Scroll to the latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Save messages to localStorage whenever they change
    useEffect(() => {
        try {
            localStorage.setItem('sparks_chat_messages', JSON.stringify(messages));
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }, [messages]);

    // Save message count to localStorage
    useEffect(() => {
        try {
            localStorage.setItem('sparks_message_count', messageCount.toString());
        } catch (error) {
            console.error('Error saving message count:', error);
        }
    }, [messageCount]);

    // Save access status to localStorage
    useEffect(() => {
        try {
            localStorage.setItem('sparks_has_access', hasAccess.toString());
        } catch (error) {
            console.error('Error saving access status:', error);
        }
    }, [hasAccess]);

    // Reset chat when user changes (login/logout/switch user)
    useEffect(() => {
        const newUserId = user?.id || null;
        
        // If user changed (different ID or logged out), reset the chat
        if (newUserId !== currentUserId) {
            console.log('User changed - resetting AI Agent chat');
            console.log('Previous user:', currentUserId);
            console.log('New user:', newUserId);
            
            // IMPORTANT: Clear localStorage FIRST before setting states
            // This prevents race conditions with other useEffects that save to localStorage
            localStorage.removeItem('sparks_chat_messages');
            localStorage.removeItem('sparks_message_count');
            localStorage.removeItem('sparks_has_access');
            localStorage.removeItem('sparks_premium_user_id');
            
            // Reset messages to initial state
            const initialMessage = {
                id: 'initial',
                role: 'model' as const,
                text: `⚡ Greetings! I'm Sparks, your expert in renewable energy. I'm here to help you navigate location analysis, resource estimation, and cost evaluation for your renewable energy site selector system. What brilliant question do you have for me today?`,
                sources: []
            };
            
            // Update all states - these will trigger the save useEffects which will write to localStorage
            setMessages([initialMessage]);
            setMessageCount(0);
            setHasAccess(false);
            
            // Store the new user ID
            setCurrentUserId(newUserId);
            if (newUserId) {
                localStorage.setItem('sparks_current_user_id', newUserId);
            } else {
                localStorage.removeItem('sparks_current_user_id');
            }
            
            console.log('Chat reset complete - user now on FREE tier');
        }
    }, [user, currentUserId]);

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

        // Check if user needs to pay
        if (!hasAccess && messageCount >= FREE_MESSAGE_LIMIT) {
            setShowPaymentModal(true);
            return;
        }

        setIsSending(true);
        setInput('');
        setMessageCount(prev => prev + 1);

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

    const handlePaymentSuccess = () => {
        setHasAccess(true);
        
        // Store premium access with user ID to ensure it's user-specific
        const currentUser = user?.id || 'guest';
        localStorage.setItem('sparks_premium_user_id', currentUser);
        
        setMessages(prev => [...prev, {
            id: crypto.randomUUID(),
            role: 'model',
            text: '🎉 Thank you for your payment! You now have unlimited access to Sparks AI. How can I help you today?',
            sources: []
        }]);
    };

    const handleClearChat = () => {
        if (confirm('Are you sure you want to clear the chat history? This action cannot be undone.')) {
            const initialMessage: Message = { 
                id: 'initial', 
                role: 'model', 
                text: `⚡ Greetings! I'm Sparks, your expert in renewable energy. I'm here to help you navigate location analysis, resource estimation, and cost evaluation for your renewable energy site selector system. What brilliant question do you have for me today?`, 
                sources: [] 
            };
            setMessages([initialMessage]);
            // Don't reset messageCount or hasAccess - keep payment status
            localStorage.removeItem('sparks_chat_messages');
        }
    };

    return (
        <div className="relative h-screen w-full overflow-hidden bg-gray-50">
            {/* Subtle animated gradient background */}
            <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-green-50/30 to-emerald-50/20"></div>
            <div className="absolute inset-0 opacity-30">
                <div className="absolute top-20 left-10 w-72 h-72 bg-green-200 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
                <div className="absolute top-40 right-10 w-72 h-72 bg-emerald-200 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
                <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
            </div>
            
            {/* === Chat Interface Layer === */}
            <div className="relative z-10 flex flex-col h-full max-w-6xl mx-auto"> 
                <div className="flex flex-col h-full w-full bg-white/80 backdrop-blur-xl overflow-hidden shadow-2xl border-x border-gray-200/50">
                    
                    {/* === Professional Header === */}
                    <div className="sticky top-0 z-20 bg-white/95 backdrop-blur-xl border-b border-gray-200/80 shadow-sm">
                        <div className="max-w-4xl mx-auto px-6 py-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3 animate-slideInLeft">
                                    {/* Clean Logo with pulse effect */}
                                    <div className="relative">
                                        <div className="absolute inset-0 bg-green-500/20 rounded-lg animate-pulse-slow"></div>
                                        <div className="relative w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform duration-200">
                                            <Zap className="h-6 w-6 text-white" />
                                        </div>
                                    </div>
                                    <div>
                                        <h1 className="text-lg font-semibold text-gray-900 tracking-tight">Sparks AI</h1>
                                        <p className="text-xs text-gray-500 flex items-center">
                                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5 animate-pulse"></span>
                                            Online
                                        </p>
                                    </div>
                                </div>
                                
                                {/* Access Status */}
                                <div className="flex items-center space-x-3 animate-slideInRight">
                                    {/* Clear Chat Button */}
                                    {messages.length > 1 && (
                                        <button
                                            onClick={handleClearChat}
                                            className="hidden sm:flex items-center text-sm text-gray-600 hover:text-red-600 bg-gray-100 hover:bg-red-50 px-3 py-1.5 rounded-lg transition-all duration-200"
                                            title="Clear chat history"
                                        >
                                            <Trash2 className="w-3.5 h-3.5 mr-1" />
                                            Clear
                                        </button>
                                    )}
                                    
                                    {!hasAccess && (
                                        <>
                                            <div className="hidden sm:flex items-center text-sm text-gray-600 bg-gray-100 px-3 py-1.5 rounded-lg hover:bg-gray-200 transition-colors duration-200">
                                                <span className="font-medium">{FREE_MESSAGE_LIMIT - messageCount}</span>
                                                <span className="ml-1 text-gray-500">free messages</span>
                                            </div>
                                            <button
                                                onClick={() => setShowPaymentModal(true)}
                                                className="group relative bg-gradient-to-r from-green-500 to-emerald-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:from-green-600 hover:to-emerald-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 overflow-hidden"
                                            >
                                                <span className="relative z-10 flex items-center">
                                                    <Zap className="w-4 h-4 mr-1.5" />
                                                    Upgrade
                                                </span>
                                                <div className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-green-600 opacity-0 group-hover:opacity-100 transition-opacity duration-200"></div>
                                            </button>
                                        </>
                                    )}
                                    {hasAccess && (
                                        <div className="flex items-center text-sm text-green-700 bg-gradient-to-r from-green-50 to-emerald-50 px-4 py-1.5 rounded-lg border border-green-200 shadow-sm">
                                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                                            <span className="font-medium">Premium</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* === Messages Area === */}
                    <div className="flex-1 overflow-y-auto custom-scrollbar bg-transparent"> 
                        <div className="max-w-4xl mx-auto px-6 py-8">
                            {messages.length === 1 && (
                                <div className="text-center py-20 animate-fadeInUp">
                                    <div className="relative inline-flex items-center justify-center mb-8">
                                        <div className="absolute inset-0 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full blur-2xl opacity-20 animate-pulse-slow"></div>
                                        <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-2xl animate-float">
                                            <Zap className="w-12 h-12 text-white" />
                                        </div>
                                    </div>
                                    <h2 className="text-3xl font-bold text-gray-900 mb-3 animate-slideInUp">Welcome to Sparks AI</h2>
                                    <p className="text-gray-600 mb-16 max-w-lg mx-auto text-lg animate-slideInUp animation-delay-200">Your intelligent assistant for renewable energy analysis, site selection, and cost evaluation.</p>
                                    
                                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-3xl mx-auto">
                                        <button 
                                            className="group text-left p-6 bg-white/90 backdrop-blur-sm rounded-2xl border border-gray-200 hover:border-green-500 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 animate-slideInUp animation-delay-300"
                                            onClick={() => setInput("What are the best locations for solar energy?")}
                                        >
                                            <div className="text-4xl mb-3 transform group-hover:scale-110 transition-transform duration-300">☀️</div>
                                            <p className="font-semibold text-gray-900 mb-2 text-lg group-hover:text-green-600 transition-colors">Location Analysis</p>
                                            <p className="text-sm text-gray-500 leading-relaxed">Find optimal sites for renewable energy projects</p>
                                            <div className="mt-3 flex items-center text-green-600 text-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                                <span>Explore</span>
                                                <svg className="w-4 h-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                </svg>
                                            </div>
                                        </button>
                                        <button 
                                            className="group text-left p-6 bg-white/90 backdrop-blur-sm rounded-2xl border border-gray-200 hover:border-green-500 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 animate-slideInUp animation-delay-500"
                                            onClick={() => setInput("How much energy can I generate?")}
                                        >
                                            <div className="text-4xl mb-3 transform group-hover:scale-110 transition-transform duration-300">⚡</div>
                                            <p className="font-semibold text-gray-900 mb-2 text-lg group-hover:text-green-600 transition-colors">Resource Estimation</p>
                                            <p className="text-sm text-gray-500 leading-relaxed">Calculate energy generation potential</p>
                                            <div className="mt-3 flex items-center text-green-600 text-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                                <span>Calculate</span>
                                                <svg className="w-4 h-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                </svg>
                                            </div>
                                        </button>
                                        <button 
                                            className="group text-left p-6 bg-white/90 backdrop-blur-sm rounded-2xl border border-gray-200 hover:border-green-500 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 animate-slideInUp animation-delay-700"
                                            onClick={() => setInput("What's the cost of a solar installation?")}
                                        >
                                            <div className="text-4xl mb-3 transform group-hover:scale-110 transition-transform duration-300">💰</div>
                                            <p className="font-semibold text-gray-900 mb-2 text-lg group-hover:text-green-600 transition-colors">Cost Evaluation</p>
                                            <p className="text-sm text-gray-500 leading-relaxed">Estimate project expenses and ROI</p>
                                            <div className="mt-3 flex items-center text-green-600 text-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                                <span>Estimate</span>
                                                <svg className="w-4 h-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                </svg>
                                            </div>
                                        </button>
                                    </div>
                                </div>
                            )}
                            
                            {messages.map((message) => (
                                <ChatBubble key={message.id} message={message} />
                            ))}
                            <div ref={messagesEndRef} />
                        </div>
                    </div>

                    {/* === Modern Input Area === */}
                    <div className="sticky bottom-0 z-20 bg-white/95 backdrop-blur-xl border-t border-gray-200/80 shadow-2xl">
                        <div className="max-w-4xl mx-auto px-6 py-5">
                            <div className="relative flex items-center bg-white rounded-2xl border-2 border-gray-200 focus-within:border-green-500 focus-within:ring-4 focus-within:ring-green-500/10 transition-all duration-300 shadow-lg hover:shadow-xl">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Ask Sparks anything about renewable energy..."
                                    disabled={isSending}
                                    className="w-full px-6 py-4 text-[15px] bg-transparent text-gray-900 focus:outline-none placeholder-gray-400"
                                />
                                <button
                                    onClick={handleSend}
                                    disabled={isSending || !input.trim()}
                                    className={`mr-2 p-3 rounded-xl transition-all duration-300 ${
                                        isSending || !input.trim()
                                            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                            : 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white shadow-lg hover:shadow-2xl transform hover:scale-110 active:scale-95'
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
                            <div className="flex items-center justify-between mt-3 px-2">
                                <p className="text-xs text-gray-500 flex items-center animate-fadeIn">
                                    <CornerDownLeft className="w-3.5 h-3.5 mr-1.5 opacity-60" />
                                    Press Enter to send your message
                                </p>
                                <p className="text-xs text-gray-400 flex items-center animate-fadeIn animation-delay-200">
                                    <span className="hidden sm:inline mr-1">Powered by</span>
                                    <span className="font-medium text-green-600">Gemini AI</span>
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* === Custom Styles === */}
                    <style>{`
                        @keyframes fadeIn {
                            from { opacity: 0; transform: translateY(10px); }
                            to { opacity: 1; transform: translateY(0); }
                        }
                        
                        @keyframes fadeInUp {
                            from { opacity: 0; transform: translateY(30px); }
                            to { opacity: 1; transform: translateY(0); }
                        }
                        
                        @keyframes slideInUp {
                            from { opacity: 0; transform: translateY(20px); }
                            to { opacity: 1; transform: translateY(0); }
                        }
                        
                        @keyframes slideInLeft {
                            from { opacity: 0; transform: translateX(-20px); }
                            to { opacity: 1; transform: translateX(0); }
                        }
                        
                        @keyframes slideInRight {
                            from { opacity: 0; transform: translateX(20px); }
                            to { opacity: 1; transform: translateX(0); }
                        }
                        
                        @keyframes float {
                            0%, 100% { transform: translateY(0px); }
                            50% { transform: translateY(-10px); }
                        }
                        
                        @keyframes blob {
                            0%, 100% { transform: translate(0, 0) scale(1); }
                            25% { transform: translate(20px, -20px) scale(1.05); }
                            50% { transform: translate(-20px, 20px) scale(0.95); }
                            75% { transform: translate(20px, 20px) scale(1.05); }
                        }
                        
                        @keyframes pulse-slow {
                            0%, 100% { opacity: 0.5; transform: scale(1); }
                            50% { opacity: 0.8; transform: scale(1.05); }
                        }
                        
                        .animate-fadeIn {
                            animation: fadeIn 0.6s ease-out;
                        }
                        
                        .animate-fadeInUp {
                            animation: fadeInUp 0.8s ease-out;
                        }
                        
                        .animate-slideInUp {
                            animation: slideInUp 0.6s ease-out;
                        }
                        
                        .animate-slideInLeft {
                            animation: slideInLeft 0.6s ease-out;
                        }
                        
                        .animate-slideInRight {
                            animation: slideInRight 0.6s ease-out;
                        }
                        
                        .animate-float {
                            animation: float 3s ease-in-out infinite;
                        }
                        
                        .animate-blob {
                            animation: blob 8s infinite;
                        }
                        
                        .animate-pulse-slow {
                            animation: pulse-slow 3s ease-in-out infinite;
                        }
                        
                        .animation-delay-200 {
                            animation-delay: 0.2s;
                        }
                        
                        .animation-delay-300 {
                            animation-delay: 0.3s;
                        }
                        
                        .animation-delay-500 {
                            animation-delay: 0.5s;
                        }
                        
                        .animation-delay-700 {
                            animation-delay: 0.7s;
                        }
                        
                        .animation-delay-2000 {
                            animation-delay: 2s;
                        }
                        
                        .animation-delay-4000 {
                            animation-delay: 4s;
                        }
                        
                        .custom-scrollbar::-webkit-scrollbar {
                            width: 8px;
                        }
                        .custom-scrollbar::-webkit-scrollbar-track {
                            background: transparent;
                        }
                        .custom-scrollbar::-webkit-scrollbar-thumb {
                            background: linear-gradient(180deg, #d1d5db, #9ca3af);
                            border-radius: 10px;
                        }
                        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                            background: linear-gradient(180deg, #9ca3af, #6b7280);
                        }
                    `}</style>
                </div>
            </div>

            {/* Payment Modal */}
            <StripePaymentModal
                isOpen={showPaymentModal}
                onClose={() => setShowPaymentModal(false)}
                onPaymentSuccess={handlePaymentSuccess}
            />
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


