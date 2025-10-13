import React, { useState, useEffect } from 'react';
import { X, CreditCard, Lock } from 'lucide-react';
import { loadStripe, StripeElementsOptions } from '@stripe/stripe-js';
import {
    Elements,
    CardElement,
    useStripe,
    useElements
} from '@stripe/react-stripe-js';

interface StripePaymentModalProps {
    isOpen: boolean;
    onClose: () => void;
    onPaymentSuccess: () => void;
}

// Initialize Stripe outside component to avoid recreating on every render
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '');

const CARD_ELEMENT_OPTIONS = {
    style: {
        base: {
            color: '#1f2937',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: '#9ca3af',
            },
        },
        invalid: {
            color: '#ef4444',
            iconColor: '#ef4444',
        },
    },
};

const CheckoutForm: React.FC<{
    onSuccess: () => void;
    onClose: () => void;
}> = ({ onSuccess, onClose }) => {
    const stripe = useStripe();
    const elements = useElements();
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [selectedPlan, setSelectedPlan] = useState<'weekly' | 'monthly' | 'yearly'>('monthly');

    // Plan pricing
    const plans = {
        weekly: { amount: 4.99, label: 'Weekly', savings: '' },
        monthly: { amount: 14.99, label: 'Monthly', savings: '' },
        yearly: { amount: 99.99, label: 'Yearly', savings: 'Save 44%' }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!stripe || !elements) {
            return;
        }

        setIsProcessing(true);
        setError(null);

        try {
            // Create payment intent on the backend
            const response = await fetch('http://localhost:8000/api/v1/stripe/create-payment-intent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plan: selectedPlan,
                    currency: 'usd',
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to create payment intent');
            }

            const { client_secret } = await response.json();

            // Confirm the payment with Stripe
            const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(
                client_secret,
                {
                    payment_method: {
                        card: elements.getElement(CardElement)!,
                        billing_details: {
                            name: name,
                            email: email,
                        },
                    },
                }
            );

            if (stripeError) {
                setError(stripeError.message || 'Payment failed');
                setIsProcessing(false);
                return;
            }

            if (paymentIntent.status === 'succeeded') {
                // Payment successful
                onSuccess();
                onClose();
                // Reset form
                setEmail('');
                setName('');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Plan Selection */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                    Select Your Plan
                </label>
                <div className="grid grid-cols-3 gap-3">
                    {Object.entries(plans).map(([key, plan]) => (
                        <button
                            key={key}
                            type="button"
                            onClick={() => setSelectedPlan(key as 'weekly' | 'monthly' | 'yearly')}
                            className={`relative p-4 border-2 rounded-lg transition-all ${
                                selectedPlan === key
                                    ? 'border-green-500 bg-green-50'
                                    : 'border-gray-200 hover:border-green-300'
                            }`}
                        >
                            {plan.savings && (
                                <span className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full whitespace-nowrap">
                                    {plan.savings}
                                </span>
                            )}
                            <div className="text-center">
                                <div className="text-sm font-medium text-gray-900">{plan.label}</div>
                                <div className="text-lg font-bold text-gray-900 mt-1">
                                    ${plan.amount}
                                </div>
                                <div className="text-xs text-gray-500">per {key === 'yearly' ? 'year' : key === 'monthly' ? 'month' : 'week'}</div>
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Email */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                </label>
                <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                    placeholder="you@example.com"
                />
            </div>

            {/* Card Holder Name */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cardholder Name
                </label>
                <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                    placeholder="John Doe"
                />
            </div>

            {/* Card Element */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Card Information
                </label>
                <div className="w-full px-4 py-3 border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-green-500 focus-within:border-transparent transition-all">
                    <CardElement options={CARD_ELEMENT_OPTIONS} />
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                    {error}
                </div>
            )}

            {/* Security Notice */}
            <div className="bg-gray-50 p-3 rounded-lg flex items-start space-x-2">
                <Lock className="h-4 w-4 text-gray-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-gray-600">
                    Your payment information is encrypted and secure. We use industry-standard security measures.
                </p>
            </div>

            {/* Submit Button */}
            <button
                type="submit"
                disabled={!stripe || isProcessing}
                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 focus:ring-4 focus:ring-green-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
                {isProcessing ? (
                    <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Processing...</span>
                    </>
                ) : (
                    <>
                        <CreditCard className="h-5 w-5" />
                        <span>Pay ${plans[selectedPlan].amount}</span>
                    </>
                )}
            </button>

            {/* Terms */}
            <p className="text-xs text-gray-500 text-center">
                By confirming your payment, you agree to our{' '}
                <a href="#" className="text-green-600 hover:underline">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-green-600 hover:underline">Privacy Policy</a>
            </p>
        </form>
    );
};

const StripePaymentModal: React.FC<StripePaymentModalProps> = ({ 
    isOpen, 
    onClose, 
    onPaymentSuccess 
}) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-6 rounded-t-2xl relative">
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 text-white hover:bg-white/20 rounded-full p-2 transition-colors"
                    >
                        <X className="h-5 w-5" />
                    </button>
                    <div className="flex items-center space-x-3">
                        <div className="bg-white/20 p-3 rounded-full">
                            <CreditCard className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-white">Premium Access</h2>
                            <p className="text-green-100 text-sm">Choose your subscription plan</p>
                        </div>
                    </div>
                </div>

                {/* Payment Form with Stripe Elements */}
                <Elements stripe={stripePromise}>
                    <CheckoutForm onSuccess={onPaymentSuccess} onClose={onClose} />
                </Elements>
            </div>
        </div>
    );
};

export default StripePaymentModal;
