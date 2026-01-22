import React, { useState, useEffect, useContext } from 'react';
import AuthContext from '../context/AuthContext';
import api from '../api';
import { CreditCard, AlertCircle, Loader2, CheckCircle, User, Banknote } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const PaymentForm = () => {
    const { user } = useContext(AuthContext);
    const [amount, setAmount] = useState('');
    const [userId, setUserId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [users, setUsers] = useState([]);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (user && user.role === 'Student') {
            setUserId(user.user_id); // Assuming user object has user_id or id from jwt
        }
    }, [user]);

    useEffect(() => {
        if (user && user.role === 'Admin') {
            api.get('users/')
                .then(res => setUsers(res.data))
                .catch(err => console.error("Failed to fetch users", err));
        }

        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        document.body.appendChild(script);
    }, [user]);

    const handlePayment = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const orderRes = await api.post('payment/create/', {
                user_id: userId,
                amount: amount
            });

            const { razorpay_order_id, razorpay_key_id, amount: orderAmount, currency, user_name, user_email, user_phone } = orderRes.data;

            const options = {
                key: razorpay_key_id,
                amount: orderAmount,
                currency: currency,
                name: "PayMaster",
                description: "Course Fee Payment",
                order_id: razorpay_order_id,
                handler: async function (response) {
                    try {
                        const verifyRes = await api.post('payment/status/', {
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature
                        });
                        setSuccess(true);
                        setAmount('');
                        setTimeout(() => setSuccess(false), 5000);
                    } catch (err) {
                        setError("Payment Verification Failed");
                    }
                },
                prefill: { name: user_name, email: user_email, contact: user_phone },
                theme: { color: "#4F46E5" }
            };

            const rzp1 = new window.Razorpay(options);
            rzp1.on('payment.failed', function (response) {
                setError(response.error.description);
            });
            rzp1.open();

        } catch (err) {
            setError(err.response?.data?.error || "Something went wrong payment creation");
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-md mx-auto"
        >
            <div className="card-glass p-8 relative overflow-hidden">
                {/* Decorative Elements */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl -mr-16 -mt-16 pointer-events-none"></div>
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-purple-500/10 rounded-full blur-xl -ml-12 -mb-12 pointer-events-none"></div>

                <div className="relative z-10">
                    <div className="flex items-center justify-center mb-8">
                        <div className="p-4 bg-indigo-50 rounded-2xl shadow-inner">
                            <CreditCard className="h-10 w-10 text-indigo-600" />
                        </div>
                    </div>

                    <div className="text-center mb-8">
                        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700">
                            Secure Payment
                        </h2>
                        <p className="text-slate-500 text-sm mt-1">Complete your transaction securely</p>
                    </div>

                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 flex items-start gap-3 text-sm border border-red-100"
                            >
                                <AlertCircle className="h-5 w-5 shrink-0" />
                                <p>{error}</p>
                            </motion.div>
                        )}

                        {success && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="bg-green-50 text-green-700 p-4 rounded-xl mb-6 flex items-center gap-3 text-sm border border-green-100"
                            >
                                <CheckCircle className="h-5 w-5 shrink-0" />
                                <p>Payment Successful!</p>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <form onSubmit={handlePayment} className="space-y-6">
                        {user && user.role === 'Admin' && (
                            <div className="space-y-2">
                                <label className="text-sm font-semibold text-slate-700 ml-1">Select Student</label>
                                <div className="relative group">
                                    <User className="absolute left-4 top-3.5 h-5 w-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                    <select
                                        value={userId}
                                        onChange={(e) => setUserId(e.target.value)}
                                        className="input-field pl-12 appearance-none"
                                        required
                                    >
                                        <option value="">Choose a student...</option>
                                        {users.map(u => (
                                            <option key={u.id} value={u.id}>{u.full_name}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-slate-700 ml-1">Amount</label>
                            <div className="relative group">
                                <Banknote className="absolute left-4 top-3.5 h-5 w-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    className="input-field pl-12"
                                    placeholder="0.00"
                                    min="1"
                                    required
                                />
                                <span className="absolute right-4 top-3.5 text-slate-400 font-medium text-sm">INR</span>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full btn-primary flex justify-center items-center gap-2 mt-4"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="h-5 w-5 animate-spin" /> Processing...
                                </>
                            ) : (
                                <>
                                    Pay Now <CreditCard className="h-5 w-5" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 pt-6 border-t border-slate-100 flex justify-center gap-4 text-slate-400 grayscale opacity-60">
                        {/* Mock Payment Icons */}
                        <div className="h-6 w-10 bg-slate-200 rounded"></div>
                        <div className="h-6 w-10 bg-slate-200 rounded"></div>
                        <div className="h-6 w-10 bg-slate-200 rounded"></div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default PaymentForm;
