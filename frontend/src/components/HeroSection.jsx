import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ShieldCheck, Zap, PieChart } from 'lucide-react';
import { Link } from 'react-router-dom';

const HeroSection = () => {
    return (
        <div className="relative overflow-hidden pt-32 pb-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">

                    {/* Text Content */}
                    <motion.div
                        initial={{ opacity: 0, x: -50 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                    >
                        <h1 className="text-5xl md:text-7xl font-extrabold pb-2 bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-indigo-800 to-indigo-600 leading-tight">
                            Smart Payments <br /> for  <span className="text-indigo-600">Smart Students</span>
                        </h1>
                        <p className="mt-6 text-xl text-slate-600 leading-relaxed max-w-lg">
                            Manage your course fees, track EMI schedules, and make secure payments seamlessly.
                        </p>

                        <div className="mt-10 flex flex-wrap gap-4">
                            <Link to="/payment" className="btn-primary flex items-center gap-2 group shadow-xl shadow-indigo-500/30">
                                Make a Payment
                                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                            </Link>
                            <Link to="/emi" className="btn-secondary">
                                View EMI Options
                            </Link>
                        </div>

                        <div className="mt-12 flex items-center gap-6 text-sm font-medium text-slate-500">
                            <div className="flex items-center gap-2">
                                <ShieldCheck className="h-5 w-5 text-emerald-500" /> Secure
                            </div>
                            <div className="flex items-center gap-2">
                                <Zap className="h-5 w-5 text-amber-500" /> Fast
                            </div>
                            <div className="flex items-center gap-2">
                                <PieChart className="h-5 w-5 text-blue-500" /> Transparent
                            </div>
                        </div>
                    </motion.div>

                    {/* Visual/Image */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, rotate: 5 }}
                        animate={{ opacity: 1, scale: 1, rotate: 0 }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="relative"
                    >
                        {/* Abstract Background Blurs */}
                        <div className="absolute -top-20 -right-20 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
                        <div className="absolute -bottom-20 -left-20 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>

                        {/* Card Mockup */}
                        <div className="card-glass p-8 rotate-3 hover:rotate-0 transition-transform duration-500">
                            <div className="flex justify-between items-center mb-8">
                                <div className="h-12 w-12 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-xl">P</div>
                                <div className="text-right">
                                    <p className="text-xs text-slate-400 uppercase tracking-widest">Balance Due</p>
                                    <p className="text-2xl font-bold text-slate-900">₹ 45,000</p>
                                </div>
                            </div>
                            <div className="space-y-4">
                                <div className="h-4 bg-slate-100 rounded w-3/4"></div>
                                <div className="h-4 bg-slate-100 rounded w-1/2"></div>
                                <div className="h-4 bg-slate-100 rounded w-full"></div>
                            </div>
                            <div className="mt-8 pt-6 border-t border-slate-100 flex justify-between items-center">
                                <div className="text-sm text-slate-500">Next EMI: <span className="text-slate-900 font-semibold">15th Aug</span></div>
                                <button className="bg-slate-900 text-white px-4 py-2 rounded-lg text-sm font-medium">Pay Now</button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default HeroSection;
