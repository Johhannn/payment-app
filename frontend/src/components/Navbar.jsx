import React, { useContext } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { CreditCard, Menu, X, Settings, ArrowRight, LogIn, LogOut, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import AuthContext from '../context/AuthContext';

const Navbar = () => {
    const [isOpen, setIsOpen] = React.useState(false);
    const location = useLocation();
    const { user, logoutUser } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogout = () => {
        logoutUser();
        navigate('/login');
    };

    const links = [
        { name: 'Home', path: '/' },
        { name: 'Make Payment', path: '/payment' },
        { name: 'EMI Schedule', path: '/emi' },
    ];

    if (user && user.role === 'Admin') {
        links.push({ name: 'Users', path: '/users' });
    }

    return (
        <nav className="fixed w-full z-50 top-0 left-0 px-4 py-4">
            <div className="max-w-7xl mx-auto card-glass px-6 py-3 flex justify-between items-center">

                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 group">
                    <div className="bg-gradient-to-tr from-indigo-600 to-violet-600 text-white p-2 rounded-lg group-hover:shadow-lg group-hover:shadow-indigo-500/40 transition-all duration-300">
                        <CreditCard className="h-6 w-6" />
                    </div>
                    <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-600">
                        PayMaster
                    </span>
                </Link>

                {/* Desktop Menu */}
                <div className="hidden md:flex items-center gap-1">
                    {links.map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            className={clsx(
                                "relative px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200",
                                location.pathname === link.path
                                    ? "text-indigo-600"
                                    : "text-slate-600 hover:text-indigo-600"
                            )}
                        >
                            {location.pathname === link.path && (
                                <motion.div
                                    layoutId="navbar-indicator"
                                    className="absolute inset-0 bg-indigo-50 rounded-lg -z-10"
                                    initial={false}
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                />
                            )}
                            {link.name}
                        </Link>
                    ))}
                </div>

                {/* Actions */}
                <div className="hidden md:flex items-center gap-3">
                    {user ? (
                        <>
                            <div className="flex items-center gap-2 text-sm text-slate-600 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200">
                                <User className="h-4 w-4" />
                                <span className="font-medium text-slate-900">{user.email ? user.email.split('@')[0] : 'User'}</span>
                            </div>
                            <button onClick={handleLogout} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors" title="Logout">
                                <LogOut className="h-5 w-5" />
                            </button>
                        </>
                    ) : (
                        <Link to="/login" className="btn-primary py-2 px-4 text-sm flex items-center gap-2">
                            Login <LogIn className="h-4 w-4" />
                        </Link>
                    )}
                </div>

                {/* Mobile Toggle */}
                <div className="md:hidden">
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="p-2 text-slate-600 hover:text-indigo-600 transition-colors"
                    >
                        {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -20, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="absolute top-20 left-4 right-4 card-glass p-4 md:hidden flex flex-col gap-2 origin-top"
                    >
                        {links.map((link) => (
                            <Link
                                key={link.path}
                                to={link.path}
                                onClick={() => setIsOpen(false)}
                                className={clsx(
                                    "px-4 py-3 rounded-lg text-sm font-medium transition-colors",
                                    location.pathname === link.path
                                        ? "bg-indigo-50 text-indigo-600"
                                        : "text-slate-600 hover:bg-slate-50"
                                )}
                            >
                                {link.name}
                            </Link>
                        ))}
                        {user ? (
                            <button onClick={handleLogout} className="w-full text-left px-4 py-3 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 flex items-center gap-2">
                                <LogOut className="h-4 w-4" /> Logout
                            </button>
                        ) : (
                            <Link to="/login" onClick={() => setIsOpen(false)} className="w-full block text-center px-4 py-3 rounded-lg text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700">
                                Login
                            </Link>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};

export default Navbar;
