import React, { useState, useMemo } from 'react';
import { Language, AppView, ChatMessage, GroundingChunk, DiagnosisSuggestion } from './types';
import { TEXTS, ICONS, NAV_ITEMS } from './constants';
import FeatureCard from './components/FeatureCard';
import LanguageSelector from './components/LanguageSelector';
import Loader from './components/Loader';
import { DiseaseModal } from './components/DiseaseModal';
import { LoginPage } from './components/LoginPage';
import MetricsPanel from './components/MetricsPanel';
import EvaluationMetricsDisplay from './components/EvaluationMetricsDisplay';
import MedicineFinder from './components/MedicineFinder';
// import EmergencySOS from './components/EmergencySOS';
// import VideoConsult from './components/VideoConsult';
// import HealthRecord from './components/HealthRecord';

const API_BASE_URL = 'http://localhost:5000/api';

// --- Feature Components ---

const ChatbotView: React.FC<{ texts: { [key: string]: string }, language: Language }> = ({ texts, language }) => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedDisease, setSelectedDisease] = useState<string | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [analysisData, setAnalysisData] = useState<any>(null);
    const [evaluationMetrics, setEvaluationMetrics] = useState<any>(null);
    const [showMetrics, setShowMetrics] = useState(false);
    const [mlComparison, setMlComparison] = useState<any>(null);

    // Load ML comparison data on mount
    React.useEffect(() => {
        const loadMLComparison = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/ml-comparison`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.status === 'success') {
                        setMlComparison(data.data);
                    }
                }
            } catch (err) {
                console.log('ML comparison data not available');
            }
        };
        loadMLComparison();
    }, []);

    // Initialize with greeting messages
    React.useEffect(() => {
        if (messages.length === 0) {
            const greetingMessages: ChatMessage[] = [
                {
                    sender: 'bot',
                    text: 'greeting'
                }
            ];
            setMessages(greetingMessages);
        }
    }, []);

    const handleSend = async () => {
        if (!input.trim()) return;
        
        const userMessage: ChatMessage = { sender: 'user', text: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input,
                    language: language
                })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success && data.result) {
                setAnalysisData(data.result);
                // Store evaluation metrics
                if (data.evaluation_metrics) {
                    setEvaluationMetrics(data.evaluation_metrics);
                    setShowMetrics(false);
                }
                const botMessage: ChatMessage = { sender: 'bot', text: 'structured_result' };
                setMessages(prev => [...prev, botMessage]);
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        } catch (err) {
            console.error("Chat error:", err);
            const errorMsg = err instanceof Error ? err.message : 'An error occurred while processing your request.';
            setError(errorMsg);
            const errorMessage: ChatMessage = { 
                sender: 'bot', 
                text: `Sorry, I encountered an error: ${errorMsg}. Please ensure the API server is running on port 5000.` 
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleVoiceTranscript = (text: string, detectedLanguage: Language) => {
        setInput(text);
        // Auto-send after voice input
        setTimeout(() => {
            setMessages(prev => [...prev, { sender: 'user', text: text }]);
            setInput('');
            setIsLoading(true);
            setError(null);

            fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    language: detectedLanguage
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.result) {
                    setAnalysisData(data.result);
                    setMessages(prev => [...prev, { sender: 'bot', text: 'structured_result' }]);
                }
                setIsLoading(false);
            })
            .catch(err => {
                console.error('Voice processing error:', err);
                setIsLoading(false);
                setError('Could not process voice input');
            });
        }, 500);
    };

    const getUrgencyColor = (color: string) => {
        switch (color) {
            case 'red':
                return 'border-emergency-300 bg-emergency-50 dark:bg-emergency-900/30';
            case 'amber':
                return 'border-warning-300 bg-warning-50 dark:bg-warning-900/30';
            case 'yellow':
                return 'border-warning-300 bg-warning-50 dark:bg-warning-900/30';
            case 'green':
                return 'border-health-300 bg-health-50 dark:bg-health-900/30';
            default:
                return 'border-neutral-300 bg-neutral-50 dark:bg-neutral-100/30';
        }
    };

    const getUrgencyTextColor = (color: string) => {
        switch (color) {
            case 'red':
                return 'text-emergency-800 dark:text-emergency-200';
            case 'amber':
                return 'text-warning-800 dark:text-warning-200';
            case 'yellow':
                return 'text-warning-800 dark:text-warning-200';
            case 'green':
                return 'text-health-800 dark:text-health-200';
            default:
                return 'text-blue-900 dark:text-blue-900';
        }
    };

    return (
        <div className="p-4 flex flex-col h-full">
            <DiseaseModal
                diseaseLabel={selectedDisease || ''}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                language={language}
            />

            {error && (
                <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border-l-4 border-red-500 text-red-800 dark:text-red-200 rounded">
                    <p className="font-semibold">{texts.error || 'Error'}</p>
                    <p className="text-sm">{error}</p>
                </div>
            )}
            
            <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900 border-l-4 border-amber-500 text-amber-800 dark:text-amber-200 rounded">
                <p className="font-semibold">{texts.disclaimer || 'Disclaimer'}</p>
                <p className="text-base">{texts.disclaimer || 'This tool provides diagnostic suggestions based on local AI analysis and is intended for informational purposes only.'}</p>
            </div>

            <div className="flex-grow overflow-y-auto bg-[#FF9500] rounded-lg p-4 space-y-4 mb-4">
                {messages.length === 0 && !isLoading && (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-6 py-8">
                        <div className="text-7xl">👋</div>
                        <div>
                            <h2 className="text-6xl font-bold text-blue-900 mb-2">
                                {language === 'HI' ? 'स्वागत है' : language === 'PA' ? 'ਸਵਾਗਤ ਹੈ' : 'Welcome'}
                            </h2>
                            <p className="text-3xl text-blue-800 mb-4">
                                {language === 'HI'
                                    ? 'अपने लक्षण बताएं और हम आपकी मदद करेंगे'
                                    : language === 'PA'
                                    ? 'ਆਪਣੇ ਲੱਛਣ ਦੱਸੋ ਅਤੇ ਅਸੀਂ ਤੁਹਾਡੀ ਮਦਦ ਕਰਾਂਗੇ'
                                    : 'Tell us about your symptoms and we will help'}
                            </p>
                        </div>



                        <p className="text-lg text-[#654321] pt-4">
                            {language === 'HI'
                                ? 'या नीचे टाइप करें'
                                : language === 'PA'
                                ? 'ਜਾਂ ਹੇਠਾਂ ਟਾਈਪ ਕਰੋ'
                                : 'Or type below'}
                        </p>
                    </div>
                )}
                
                {messages.map((msg, index) => (
                    <div key={index}>
                        {msg.sender === 'user' && (
                            <div className="flex justify-end mb-4">
                                <div className="rounded-lg p-3 max-w-md bg-primary-600 text-white shadow-md">
                                    {msg.text}
                                </div>
                            </div>
                        )}
                        
                        {msg.sender === 'bot' && msg.text === 'greeting' && (
                            <div className="bg-neutral-50 rounded-lg p-4 border border-neutral-300 mb-4 shadow-sm">
                                <div className="flex gap-3 items-start">
                                    <span className="text-4xl">👋</span>
                                    <div className="flex-1">
                                        <h3 className="font-bold text-2xl text-[#654321] mb-1">
                                            {language === 'HI' ? 'नमस्ते!' : language === 'PA' ? 'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ!' : 'Hello!'}
                                        </h3>
                                        <p className="text-xl text-[#654321]">
                                            {language === 'HI'
                                                ? 'मैं आपकी स्वास्थ्य सहायक हूँ। आप मुझसे अपने लक्षणों के बारे में बता सकते हैं। कृपया याद रखें - मैं सुझाव देता हूँ, निदान नहीं। हमेशा अपने डॉक्टर से मिलें।'
                                                : language === 'PA'
                                                ? 'ਮੈਂ ਤੁਹਾਡਾ ਸਿਹਤ ਸਹਾਇਕ ਹਾਂ। ਤੁਸੀਂ ਮੈਨੂੰ ਆਪਣੇ ਲੱਛਣਾਂ ਬਾਰੇ ਦੱਸ ਸਕਦੇ ਹੋ। ਯਾਦ ਰੱਖੋ - ਮੈਂ ਸਲਾਹ ਦਿੰਦਾ ਹਾਂ, ਨਿਦਾਨ ਨਹੀਂ। ਆਪਣੇ ਡਾਕਟਰ ਨੂੰ ਹਮੇਸ਼ਾ ਮਿਲੋ।'
                                                : "I'm your AI health assistant. Tell me about your symptoms. Remember, I suggest but don't diagnose. Always see a doctor."}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                        
                        {msg.sender === 'bot' && msg.text === 'structured_result' && analysisData && (
                            <div className="space-y-4 mb-4">
                                {/* Symptoms Section */}
                                {analysisData.symptoms_extracted && analysisData.symptoms_extracted.length > 0 && (
                                    <div className="bg-[#f7b48d] dark:bg-[#f7b48d] rounded-lg p-4 border border-[#e8a366] dark:border-[#e8a366]">
                                        <h3 className="font-bold text-2xl mb-3 text-[#6B8E23] dark:text-[#6B8E23]">📋 Extracted Symptoms</h3>
                                        <div className="flex flex-wrap gap-2">
                                            {analysisData.symptoms_extracted.map((symptom: any, idx: number) => {
                                                const name = typeof symptom === 'string' ? symptom : symptom.name || symptom;
                                                return (
                                                    <span
                                                        key={idx}
                                                        className="inline-block rounded-full bg-white text-[#6B8E23] px-4 py-2 text-2xl font-bold border-2 border-[#6B8E23]"
                                                    >
                                                        {name}
                                                    </span>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}

                                {/* Overall Triage */}
                                {analysisData.overall_triage && (
                                    <div className="bg-orange-100 dark:bg-orange-900/40 rounded-lg p-4 border-4 border-[#654321] dark:border-[#654321]">
                                        <h3 className="font-bold text-2xl mb-2 text-[#654321] dark:text-[#654321]">⚡ Overall Triage Level</h3>
                                        <p className="text-[#654321] dark:text-[#654321] font-semibold text-xl">
                                            {typeof analysisData.overall_triage === 'object' 
                                                ? analysisData.overall_triage.level 
                                                : analysisData.overall_triage}
                                        </p>
                                    </div>
                                )}

                                {/* Diseases Section */}
                                {analysisData.diagnoses && analysisData.diagnoses.length > 0 && (
                                    <div>
                                        <h3 className="font-bold text-2xl mb-3 text-[#6B8E23] dark:text-[#6B8E23]">🏥 Probable Diseases</h3>
                                        <div className="grid gap-3">
                                            {analysisData.diagnoses.map((diagnosis: any, idx: number) => {
                                                const urgency = diagnosis.urgency || {};
                                                const color = urgency.color || 'gray';
                                                return (
                                                    <div
                                                        key={idx}
                                                        className={`rounded-lg p-4 border-6 cursor-pointer transition hover:shadow-lg bg-white dark:bg-white ${getUrgencyColor(color)}`}
                                                        onClick={() => {
                                                            setSelectedDisease(diagnosis.name);
                                                            setIsModalOpen(true);
                                                        }}
                                                    >
                                                        <div className="flex items-start justify-between mb-2">
                                                            <h4 className="font-bold text-2xl text-[#6B8E23] dark:text-[#6B8E23] hover:text-[#556B2F] dark:hover:text-[#556B2F]">
                                                                {diagnosis.name}
                                                            </h4>
                                                            {urgency.level && (
                                                                <span className={`px-3 py-1 rounded-full text-sm font-semibold whitespace-nowrap ml-2 ${getUrgencyTextColor(color)}`}>
                                                                    {urgency.icon} {urgency.level}
                                                                </span>
                                                            )}
                                                        </div>
                                                        
                                                        <p className="text-xl text-[#6B8E23] dark:text-[#6B8E23] mb-2">
                                                            {urgency.reasoning || 'Disease analysis'}
                                                        </p>
                                                        
                                                        {diagnosis.score && (
                                                            <p className="text-xl font-semibold text-[#6B8E23] dark:text-[#6B8E23] mb-2">
                                                                Match Score: {Math.round(diagnosis.score * 10) / 10}%
                                                            </p>
                                                        )}
                                                        
                                                        {urgency.action && (
                                                            <div className={`text-sm font-semibold ${getUrgencyTextColor(color)} bg-opacity-20`}>
                                                                → {urgency.action}
                                                            </div>
                                                        )}

                                                        {diagnosis.precautions && diagnosis.precautions.length > 0 && (
                                                            <div className="mt-3 pt-3 border-t border-opacity-30 border-[#6B8E23]">
                                                                <p className="text-lg font-semibold text-[#6B8E23] dark:text-[#6B8E23] mb-1">Quick Precautions:</p>
                                                                <ul className="text-lg space-y-1">
                                                                    {diagnosis.precautions.slice(0, 2).map((prec: string, pidx: number) => (
                                                                        <li key={pidx} className="text-[#6B8E23] dark:text-[#6B8E23]">• {prec}</li>
                                                                    ))}
                                                                    {diagnosis.precautions.length > 2 && (
                                                                        <li className="text-[#6B8E23] dark:text-[#6B8E23] italic">+{diagnosis.precautions.length - 2} more</li>
                                                                    )}
                                                                </ul>
                                                            </div>
                                                        )}
                                                        
                                                        <p className="text-lg text-[#6B8E23] dark:text-[#6B8E23] mt-3">Click to see full details</p>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}

                                {analysisData.diagnoses && analysisData.diagnoses.length === 0 && (
                                    <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-700">
                                        <p className="text-yellow-800 dark:text-yellow-200">
                                            📊 Analysis complete. Please consult with a healthcare professional for proper diagnosis.
                                        </p>
                                    </div>
                                )}

                                {/* ML Model Comparison */}
                                {mlComparison && mlComparison.models && (
                                    <div className="bg-gradient-to-r from-[#8B6F47] to-[#6B4423] dark:from-[#5C4033] dark:to-[#3D2817] rounded-lg p-4 border border-[#A0826D] dark:border-[#5C4033]">
                                        <h3 className="font-bold text-4xl mb-4 text-white dark:text-white">🤖 ML Model Performance</h3>
                                        
                                        {/* Models Table */}
                                        <div className="overflow-x-auto mb-4">
                                            <table className="w-full text-xl">
                                                <thead>
                                                    <tr className="border-b border-[#A0826D] dark:border-[#5C4033]">
                                                        <th className="text-left py-3 px-4 font-bold text-white dark:text-white">Model</th>
                                                        <th className="text-center py-3 px-4 font-bold text-white dark:text-white">Accuracy</th>
                                                        <th className="text-center py-3 px-4 font-bold text-white dark:text-white">Precision</th>
                                                        <th className="text-center py-3 px-4 font-bold text-white dark:text-white">Recall</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {mlComparison.models.map((model: string, idx: number) => (
                                                        <tr key={idx} className="border-b border-[#8B6F47] dark:border-[#5C4033] hover:bg-[#6B4423]/50 dark:hover:bg-[#3D2817]/50">
                                                            <td className="py-3 px-4 font-bold text-white dark:text-white text-lg capitalize">{model.replace(/_/g, ' ')}</td>
                                                            <td className="text-center py-3 px-4 text-white dark:text-white font-bold text-lg">{mlComparison.accuracy[idx]}%</td>
                                                            <td className="text-center py-3 px-4 text-white dark:text-white text-lg">{mlComparison.precision[idx]}%</td>
                                                            <td className="text-center py-3 px-4 text-white dark:text-white text-lg">{mlComparison.recall[idx]}%</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                        
                                        <p className="text-lg text-white dark:text-white italic font-semibold">
                                            Best Model: <span className="font-bold">{mlComparison.models[0]}</span> with {mlComparison.accuracy[0]}% accuracy
                                        </p>
                                    </div>
                                )}

                                {/* Evaluation Metrics Button */}
                                {evaluationMetrics && (
                                    <div className="mt-4 animate-fadeIn">
                                        <button
                                            onClick={() => setShowMetrics(!showMetrics)}
                                            className="w-full bg-gradient-to-r from-[#8B6F47] to-[#6B4423] hover:from-[#9D7D54] hover:to-[#7D5433] text-white font-bold text-xl py-4 px-5 rounded-xl shadow-lg transition-all duration-300 transform hover:scale-105 hover:shadow-2xl backdrop-blur-xl border border-white/30 hover:border-white/50"
                                        >
                                            {showMetrics ? '📊 Hide Evaluation Metrics' : '📊 View Evaluation Metrics'}
                                        </button>
                                        
                                        <MetricsPanel 
                                            metrics={evaluationMetrics}
                                            isOpen={showMetrics}
                                            onClose={() => setShowMetrics(false)}
                                        />
                                    </div>
                                )}

                            </div>
                        )}
                    </div>
                ))}
                
                {isLoading && (
                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-amber-100 rounded-full flex-shrink-0">{ICONS.bot}</div>
                        <div className="bg-neutral-200 rounded-lg p-3">
                            <Loader />
                        </div>
                    </div>
                )}
            </div>

            <div className="flex items-center space-x-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSend();
                        }
                    }}
                    placeholder={texts.typeMessage || 'Type your symptoms here...'}
                    disabled={isLoading}
                    className="flex-grow p-3 border rounded-full bg-amber-50 border-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-500 disabled:opacity-50"
                />

                <button 
                    onClick={handleSend} 
                    disabled={isLoading || !input.trim()} 
                    className="bg-health-600 text-white p-3 rounded-full hover:bg-health-700 disabled:bg-health-300 transition"
                >
                    {ICONS.send}
                </button>
            </div>


        </div>
    );
};

// COMMENTED OUT: FindCareView not in use
/*
// const FindCareView: React.FC<{ texts: { [key: string]: string } }> = ({ texts }) => {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState<string | null>(null);
    const [links, setLinks] = useState<GroundingChunk[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [location, setLocation] = useState<{ latitude: number, longitude: number } | null>(null);
    const [locationError, setLocationError] = useState<string | null>(null);

    React.useEffect(() => {
        setIsLoading(true);
        navigator.geolocation.getCurrentPosition(
            (position) => {
                setLocation({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
                setIsLoading(false);
            },
            () => {
                setLocationError(texts.locationError);
                setIsLoading(false);
            }
        );
         // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [texts.locationError]);

    const handleSearch = async () => {
        if (!query.trim()) return;
        setIsLoading(true);
        setResponse('This feature requires Google Gemini API integration. Please use the local Chatbot feature instead.');
        setIsLoading(false);
    };
    
    return (
        <div className="p-4 flex flex-col h-full">
            <div className="flex items-center space-x-2 mb-4">
                 <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={texts.askLocation}
                    className="flex-grow p-3 border rounded-full bg-amber-50 border-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
                <button onClick={handleSearch} disabled={isLoading || !location} className="bg-blue-500 text-white p-3 rounded-full hover:bg-blue-600 disabled:bg-blue-300">
                    {ICONS.map}
                </button>
            </div>
            <div className="flex-grow overflow-y-auto bg-amber-50 rounded-lg p-4">
                {isLoading && <Loader />}
                {locationError && <p className="text-red-500">{locationError}</p>}
                {!location && !locationError && <p className="text-gray-500">{texts.gettingLocation}</p>}
                {response && <div className="prose dark:prose-invert text-gray-700 dark:text-gray-300">{response}</div>}
            </div>
        </div>
    );
};
// */

// COMMENTED OUT: AnalyzeReportView not in use
/*
// const AnalyzeReportView: React.FC<{ texts: { [key: string]: string } }> = ({ texts }) => {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [result, setResult] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setResult(null);
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;
        setIsLoading(true);
        setResult('This feature requires Google Gemini API integration. Please use the local Chatbot feature for medical analysis.');
        setIsLoading(false);
    };

    return (
        <div className="p-4 flex flex-col h-full">
            <div className="flex-grow overflow-y-auto bg-amber-50 rounded-lg p-4 space-y-4">
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
                    <input type="file" id="file-upload" className="hidden" accept="image/*" onChange={handleFileChange} />
                    <label htmlFor="file-upload" className="cursor-pointer text-blue-600 dark:text-blue-400 font-semibold">
                        {ICONS.upload}
                        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{texts.uploadPrompt}</p>
                    </label>
                </div>
                {preview && <img src={preview} alt="Report preview" className="max-w-full max-h-64 mx-auto rounded-lg" />}
                {file && <button onClick={handleAnalyze} disabled={isLoading} className="w-full bg-blue-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-600 disabled:bg-blue-300">{isLoading ? <Loader/> : texts.analyze}</button>}
                {result && (
                    <div>
                        <h3 className="text-xl font-bold mb-2 dark:text-white">{texts.analysisResult}</h3>
                        <div className="text-gray-700 dark:text-gray-300">{result}</div>
                    </div>
                )}
            </div>
        </div>
    );
};
// */

// COMMENTED OUT: SymptomAnalyzerView not in use
/*
// const SymptomAnalyzerView: React.FC<{ texts: { [key: string]: string } }> = ({ texts }) => {
    const [symptoms, setSymptoms] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState<DiagnosisSuggestion[] | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleAnalyze = async () => {
        if (!symptoms.trim()) return;

        setIsLoading(true);
        setResults(null);
        setError(null);
        
        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: symptoms
                })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success && data.result) {
                const diagnoses = data.result.diagnoses || [];
                
                // Convert diagnoses to DiagnosisSuggestion format
                const formattedDiagnoses: DiagnosisSuggestion[] = diagnoses.map((d: any) => ({
                    condition: typeof d === 'string' ? d : d.name || d,
                    likelihood: d.likelihood || 'Medium',
                    reasoning: d.reasoning || 'Based on symptom analysis'
                }));
                
                setResults(formattedDiagnoses);
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        } catch (err) {
            console.error("Symptom Analysis Error:", err);
            setError(err instanceof Error ? err.message : "An error occurred during analysis. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };
    
    const getLikelihoodColor = (likelihood: string) => {
        switch (likelihood.toLowerCase()) {
            case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
            case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
            case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
            default: return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
        }
    };

    return (
        <div className="p-4 flex flex-col h-full">
            <div className="mb-4 p-4 bg-yellow-50 dark:bg-gray-800 border-l-4 border-yellow-400 dark:border-yellow-600 rounded-r-lg">
                <h4 className="font-bold text-yellow-800 dark:text-yellow-200">For Professional Use Only</h4>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">{texts.disclaimer}</p>
            </div>

            <div className="flex flex-col space-y-4">
                <textarea
                    value={symptoms}
                    onChange={(e) => setSymptoms(e.target.value)}
                    placeholder={texts.enterSymptoms}
                    className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[120px]"
                    rows={5}
                />
                <button
                    onClick={handleAnalyze}
                    disabled={isLoading || !symptoms.trim()}
                    className="w-full bg-blue-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-600 disabled:bg-blue-300 flex justify-center items-center"
                >
                    {isLoading ? <Loader /> : texts.analyzeSymptoms}
                </button>
            </div>
            
            <div className="mt-6 flex-grow overflow-y-auto">
                {error && <p className="text-red-500 text-center">{error}</p>}
                {results && (
                    <div>
                        <h3 className="text-xl font-bold mb-4 dark:text-white">{texts.analysisResults}</h3>
                        <div className="space-y-4">
                            {results.map((result, index) => (
                                <div key={index} className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
                                    <div className="flex justify-between items-center mb-2">
                                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white">{result.condition}</h4>
                                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getLikelihoodColor(result.likelihood)}`}>
                                            {result.likelihood}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-300">{result.reasoning}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
// */


// --- Main App Component ---

const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState<{ name: string; phone: string } | null>(null);
  const [currentView, setCurrentView] = useState<AppView>(AppView.DASHBOARD);
  const [language, setLanguage] = useState<Language>(Language.EN);
  const texts = useMemo(() => TEXTS[language], [language]);

  const handleLogin = (phone: string, name: string) => {
    setCurrentUser({ name, phone });
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
    setCurrentView(AppView.DASHBOARD);
  };

  const renderView = () => {
    switch (currentView) {
      case AppView.CHATBOT:
        return <ChatbotView texts={texts} language={language} />;
      case AppView.FIND_CARE:
        return <MedicineFinder texts={texts} />;
      // case AppView.ANALYZE_REPORT:
      //   return <HealthRecord />;
      // case AppView.EMERGENCY:
      //   return <EmergencySOS />;
      // case AppView.VIDEO_CONSULT:
      //   return <VideoConsult />;
      case AppView.DASHBOARD:
      default:
        return (
          <div className="p-4 md:p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {NAV_ITEMS.filter(item => item.view !== AppView.DASHBOARD).map(item => (
                <FeatureCard
                  key={item.view}
                  icon={item.icon}
                  title={texts[item.textKey]}
                  description={texts[`${item.textKey}Desc`]}
                  onClick={() => setCurrentView(item.view)}
                />
              ))}
            </div>
          </div>
        );
    }
  };

  return (
    <>
      {!isLoggedIn ? (
        <LoginPage onLogin={handleLogin} language={language} texts={texts} onLanguageChange={setLanguage} />
      ) : (
        <div className="min-h-screen flex flex-col font-sans text-blue-900 text-lg bg-amber-50">
          {/* Header */}
          <header className="sticky top-0 bg-white dark:bg-gray-800 border-b border-neutral-200 dark:border-gray-700 shadow-sm z-10">
            <div className="container mx-auto px-4 py-3 flex justify-between items-center">
              <div className="flex items-center space-x-3">
                {currentView !== AppView.DASHBOARD && (
                   <button onClick={() => setCurrentView(AppView.DASHBOARD)} className="p-2 rounded-full hover:bg-neutral-200 dark:hover:bg-gray-700">
                     {ICONS.home}
                   </button>
                )}
                <svg className="w-10 h-10" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                  {/* Blue Sky */}
                  <circle cx="100" cy="80" r="80" fill="#2E5F8A"/>
                  
                  {/* Green Trees Left */}
                  <ellipse cx="30" cy="90" rx="20" ry="25" fill="#3FA860"/>
                  <ellipse cx="20" cy="100" rx="12" ry="18" fill="#2D8C4A"/>
                  <ellipse cx="40" cy="105" rx="15" ry="20" fill="#3FA860"/>
                  
                  {/* White House */}
                  <rect x="55" y="85" width="35" height="30" fill="white" stroke="#000" strokeWidth="1.5"/>
                  
                  {/* Red Roof */}
                  <polygon points="55,85 90,85 72.5,70" fill="#DC143C" stroke="#000" strokeWidth="1.5"/>
                  
                  {/* Roof stripes */}
                  <line x1="60" y1="78" x2="75" y2="78" stroke="#A00000" strokeWidth="1.5"/>
                  <line x1="65" y1="74" x2="80" y2="74" stroke="#A00000" strokeWidth="1.5"/>
                  <line x1="70" y1="70" x2="85" y2="70" stroke="#A00000" strokeWidth="1.5"/>
                  
                  {/* House window */}
                  <rect x="62" y="92" width="8" height="8" fill="#87CEEB" stroke="#000" strokeWidth="0.8"/>
                  <line x1="66" y1="92" x2="66" y2="100" stroke="#000" strokeWidth="0.5"/>
                  <line x1="62" y1="96" x2="70" y2="96" stroke="#000" strokeWidth="0.5"/>
                  
                  {/* House door */}
                  <rect x="75" y="100" width="8" height="15" fill="#8B4513" stroke="#000" strokeWidth="0.8"/>
                  <circle cx="82" cy="107" r="1.5" fill="#FFD700"/>
                  
                  {/* Fence */}
                  <line x1="45" y1="115" x2="95" y2="115" stroke="#000" strokeWidth="1"/>
                  <line x1="50" y1="115" x2="50" y2="120" stroke="#000" strokeWidth="0.8"/>
                  <line x1="60" y1="115" x2="60" y2="120" stroke="#000" strokeWidth="0.8"/>
                  <line x1="70" y1="115" x2="70" y2="120" stroke="#000" strokeWidth="0.8"/>
                  <line x1="80" y1="115" x2="80" y2="120" stroke="#000" strokeWidth="0.8"/>
                  <line x1="90" y1="115" x2="90" y2="120" stroke="#000" strokeWidth="0.8"/>
                  
                  {/* White Clouds */}
                  <ellipse cx="120" cy="40" rx="15" ry="10" fill="white"/>
                  <ellipse cx="130" cy="38" rx="12" ry="9" fill="white"/>
                  <ellipse cx="110" cy="38" rx="10" ry="8" fill="white"/>
                  
                  <ellipse cx="160" cy="55" rx="14" ry="9" fill="white"/>
                  <ellipse cx="170" cy="53" rx="11" ry="8" fill="white"/>
                  <ellipse cx="150" cy="54" rx="10" ry="7" fill="white"/>
                  
                  {/* Yellow Fields - curved lines */}
                  <path d="M 30 120 Q 70 115 140 125" stroke="#FFD700" strokeWidth="6" fill="none"/>
                  <path d="M 25 135 Q 80 128 150 140" stroke="#F0C000" strokeWidth="6" fill="none"/>
                  <path d="M 35 150 Q 90 140 160 155" stroke="#FFD700" strokeWidth="5" fill="none"/>
                  
                  {/* Red Medical Cross */}
                  <g transform="translate(155, 120)">
                    <rect x="-18" y="-3" width="36" height="6" fill="#DC143C" stroke="#000" strokeWidth="1.5"/>
                    <rect x="-3" y="-18" width="6" height="36" fill="#DC143C" stroke="#000" strokeWidth="1.5"/>
                  </g>
                  
                  {/* Black border circle */}
                  <circle cx="100" cy="80" r="80" fill="none" stroke="#000" strokeWidth="3"/>
                </svg>
                <div>
                  <h1 className="text-3xl font-bold text-white dark:text-white">{texts.appName}</h1>
                  <p className="text-xl text-neutral-300 dark:text-gray-400">{texts.tagline}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <LanguageSelector currentLanguage={language} onLanguageChange={setLanguage} />
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm font-semibold text-neutral-600 hover:text-emergency-600 dark:text-gray-400 dark:hover:text-emergency-400"
                >
                  {language === 'EN' ? 'Logout' : language === 'HI' ? 'लॉगआउट' : 'Logout'}
                </button>
              </div>
            </div>
          </header>

          {/* Main Layout with Sidebar */}
          <div className="flex flex-1 overflow-hidden">
            {/* Main Content */}
            <main className="flex-1 overflow-auto w-full">
              <div className="container mx-auto px-4 py-4 flex flex-col h-full">
                {renderView()}
              </div>
            </main>
          </div>
        </div>
      )}
    </>
  );
};

export default App;
