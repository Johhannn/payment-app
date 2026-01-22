import React, { useState, useEffect, useContext } from 'react';
import api from '../api';
import AuthContext from '../context/AuthContext';
import { Calendar, User, Clock, CheckCircle, Percent, Banknote, ClipboardList } from 'lucide-react';
import { motion } from 'framer-motion';

const EMISchedule = () => {
    const { user } = useContext(AuthContext);
    const [loanAmount, setLoanAmount] = useState('');
    const [tenure, setTenure] = useState('');
    const [rate, setRate] = useState('');
    const [userId, setUserId] = useState('');
    const [startDate, setStartDate] = useState('');
    const [users, setUsers] = useState([]);
    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (user && user.role === 'Admin') {
            api.get('users/')
                .then(res => setUsers(res.data))
                .catch(err => console.error(err));
        }
    }, [user]);

    const createSchedule = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await api.post('emi/create/', {
                user: userId,
                total_loan: loanAmount,
                tenure_months: tenure,
                interest_rate: rate,
                first_due_date: startDate
            });
            setSchedules(res.data);
        } catch (err) {
            console.error(err);
            alert("Failed to create schedule");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between"
            >
                <div>
                    <h2 className="text-3xl font-bold text-slate-900">EMI Schedule</h2>
                    <p className="text-slate-500 mt-1">Manage loan schedules and track payments</p>
                </div>
                <div className="h-10 w-10 bg-indigo-100 rounded-xl flex items-center justify-center text-indigo-600">
                    <Calendar className="h-6 w-6" />
                </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Creation Form - Only for Admin */}
                {user && user.role === 'Admin' && (
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className="lg:col-span-1"
                    >
                        <div className="card-glass p-6 sticky top-24">
                            <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                                <ClipboardList className="h-5 w-5 text-indigo-500" />
                                Create New Schedule
                            </h3>

                            <form onSubmit={createSchedule} className="space-y-4">
                                <div className="space-y-1">
                                    <label className="text-sm font-semibold text-slate-700 ml-1">Select User</label>
                                    <div className="relative">
                                        <User className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                                        <select value={userId} onChange={e => setUserId(e.target.value)} className="input-field pl-10 appearance-none bg-white font-medium" required>
                                            <option value="">Choose User...</option>
                                            {users.map(u => <option key={u.id} value={u.id}>{u.full_name}</option>)}
                                        </select>
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <label className="text-sm font-semibold text-slate-700 ml-1">Total Loan</label>
                                    <div className="relative">
                                        <Banknote className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                                        <input type="number" value={loanAmount} onChange={e => setLoanAmount(e.target.value)} className="input-field pl-10 bg-white" placeholder="50000" required />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <label className="text-sm font-semibold text-slate-700 ml-1">Tenure</label>
                                        <div className="relative">
                                            <Clock className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                                            <input type="number" value={tenure} onChange={e => setTenure(e.target.value)} className="input-field pl-10 bg-white" placeholder="12" required />
                                        </div>
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-sm font-semibold text-slate-700 ml-1">Interest %</label>
                                        <div className="relative">
                                            <Percent className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                                            <input type="number" value={rate} onChange={e => setRate(e.target.value)} className="input-field pl-10 bg-white" placeholder="10" step="0.1" required />
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <label className="text-sm font-semibold text-slate-700 ml-1">First Due Date</label>
                                    <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="input-field bg-white" required />
                                </div>

                                <button type="submit" disabled={loading} className="w-full btn-primary mt-4">
                                    {loading ? 'Creating...' : 'Generate Schedule'}
                                </button>
                            </form>
                        </div>
                    </motion.div>
                )}

                {/* Schedule Table */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="lg:col-span-2"
                >
                    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-slate-100">
                                <thead className="bg-slate-50">
                                    <tr>
                                        <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Due Date</th>
                                        <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Amount</th>
                                        <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                                        <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-slate-50">
                                    {schedules.map((s, i) => (
                                        <motion.tr
                                            key={i}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: i * 0.05 }}
                                            className="hover:bg-slate-50/50 transition-colors"
                                        >
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-700">
                                                {new Date(s.next_due_date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-slate-900">₹{parseFloat(s.emi_amount).toLocaleString()}</td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 gap-1">
                                                    <CheckCircle className="h-3 w-3" /> Scheduled
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <button className="text-indigo-600 hover:text-indigo-900 text-sm font-medium">View</button>
                                            </td>
                                        </motion.tr>
                                    ))}
                                    {schedules.length === 0 && (
                                        <tr>
                                            <td colSpan="4" className="px-6 py-12 text-center text-slate-400">
                                                <div className="flex flex-col items-center gap-3">
                                                    <div className="p-3 bg-slate-50 rounded-full">
                                                        <Calendar className="h-6 w-6 text-slate-300" />
                                                    </div>
                                                    <p>No schedules created yet.</p>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default EMISchedule;
