// Landing.jsx - Updated with 30 Exam Types (11 Families)
import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import {
  BookOpen,
  Headphones,
  Mic,
  PenTool,
  Building,
  GraduationCap,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

// 30 EXAM TYPES organized by family
const examFamilies = [
  {
    id: 'toefl',
    name: 'TOEFL',
    icon: '🇺🇸',
    color: 'bg-blue-500',
    description: 'Leading test for North American universities',
    variants: [
      { id: 'toefl_ibt', name: 'TOEFL iBT', description: 'Internet-based test (most common)' },
      { id: 'toefl_itp', name: 'TOEFL ITP', description: 'Institutional paper-based test' },
    ]
  },
  {
    id: 'ielts',
    name: 'IELTS',
    icon: '🇬🇧',
    color: 'bg-red-500',
    description: 'World\'s most popular English test',
    variants: [
      { id: 'ielts_academic', name: 'Academic', description: 'For university admission' },
      { id: 'ielts_general', name: 'General Training', description: 'For immigration & work' },
    ]
  },
  {
    id: 'cambridge',
    name: 'Cambridge',
    icon: '🎓',
    color: 'bg-purple-500',
    description: 'European framework (A2-C2)',
    variants: [
      { id: 'cambridge_a2_key', name: 'A2 Key (KET)', description: 'Basic level' },
      { id: 'cambridge_b1_preliminary', name: 'B1 Preliminary (PET)', description: 'Intermediate' },
      { id: 'cambridge_b2_first', name: 'B2 First (FCE)', description: 'Upper-intermediate' },
      { id: 'cambridge_c1_advanced', name: 'C1 Advanced (CAE)', description: 'Advanced' },
      { id: 'cambridge_c2_proficiency', name: 'C2 Proficiency (CPE)', description: 'Mastery' },
    ]
  },
  {
    id: 'pte',
    name: 'PTE',
    icon: '⚡',
    color: 'bg-orange-500',
    description: 'Fast computer-based testing',
    variants: [
      { id: 'pte_academic', name: 'PTE Academic', description: 'For universities worldwide' },
      { id: 'pte_core', name: 'PTE Core', description: 'Canadian immigration' },
    ]
  },
  {
    id: 'oet',
    name: 'OET',
    icon: '🏥',
    color: 'bg-green-500',
    description: 'Healthcare professionals',
    variants: [
      { id: 'oet_nursing', name: 'Nursing', description: 'For nurses' },
      { id: 'oet_medicine', name: 'Medicine', description: 'For doctors' },
      { id: 'oet_dentistry', name: 'Dentistry', description: 'For dentists' },
      { id: 'oet_pharmacy', name: 'Pharmacy', description: 'For pharmacists' },
      { id: 'oet_physiotherapy', name: 'Physiotherapy', description: 'For physios' },
      { id: 'oet_veterinary', name: 'Veterinary', description: 'For vets' },
      { id: 'oet_occupational_therapy', name: 'Occupational Therapy', description: 'For OTs' },
      { id: 'oet_podiatry', name: 'Podiatry', description: 'For podiatrists' },
      { id: 'oet_radiography', name: 'Radiography', description: 'For radiographers' },
      { id: 'oet_optometry', name: 'Optometry', description: 'For optometrists' },
      { id: 'oet_speech_pathology', name: 'Speech Pathology', description: 'For speech therapists' },
      { id: 'oet_dietetics', name: 'Dietetics', description: 'For dietitians' },
    ]
  },
  {
    id: 'linguaskill',
    name: 'Linguaskill',
    icon: '🚀',
    color: 'bg-cyan-500',
    description: 'Fast, flexible Cambridge test',
    variants: [
      { id: 'linguaskill', name: 'Linguaskill', description: 'General purposes' },
      { id: 'linguaskill_business', name: 'Linguaskill Business', description: 'Workplace contexts' },
    ]
  },
  {
    id: 'toeic',
    name: 'TOEIC',
    icon: '💼',
    color: 'bg-indigo-500',
    description: 'Business English proficiency',
    variants: [
      { id: 'toeic', name: 'TOEIC', description: 'Workplace English' },
    ]
  },
  {
    id: 'celpip',
    name: 'CELPIP',
    icon: '🍁',
    color: 'bg-red-600',
    description: 'Canadian immigration test',
    variants: [
      { id: 'celpip', name: 'CELPIP', description: 'Canadian citizenship' },
    ]
  },
  {
    id: 'trinity',
    name: 'Trinity ISE',
    icon: '🏛️',
    color: 'bg-gray-600',
    description: 'Trinity College London exam',
    variants: [
      { id: 'trinity_ise', name: 'Trinity ISE', description: 'Integrated Skills in English' },
    ]
  },
  {
    id: 'oxford',
    name: 'Oxford Test',
    icon: '📚',
    color: 'bg-blue-700',
    description: 'Oxford University Press exam',
    variants: [
      { id: 'oxford_test', name: 'Oxford Test', description: 'Modular online test' },
    ]
  },
  {
    id: 'aptis',
    name: 'APTIS',
    icon: '🌐',
    color: 'bg-teal-600',
    description: 'British Council exam',
    variants: [
      { id: 'aptis', name: 'APTIS', description: 'Flexible English test' },
    ]
  }
];

const ExamFamilyCard = ({ family }) => {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <Card className="card-duo p-6 hover:shadow-xl transition-all">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-14 h-14 ${family.color} rounded-xl flex items-center justify-center text-2xl`}>
            {family.icon}
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">{family.name}</h3>
            <p className="text-sm text-gray-600">{family.description}</p>
          </div>
        </div>
        <Badge className="bg-purple-100 text-purple-800">
          {family.variants.length} {family.variants.length > 1 ? 'variants' : 'variant'}
        </Badge>
      </div>
      
      <Button
        variant="ghost"
        size="sm"
        className="w-full justify-between text-gray-700 hover:bg-gray-100"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="font-medium">
          {expanded ? 'Hide variants' : `View ${family.variants.length} variant${family.variants.length > 1 ? 's' : ''}`}
        </span>
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </Button>
      
      {expanded && (
        <div className="mt-4 space-y-2 animate-in slide-in-from-top-2">
          {family.variants.map((variant) => (
            <div key={variant.id} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="font-medium text-gray-900">{variant.name}</div>
              <div className="text-sm text-gray-600">{variant.description}</div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

const Landing = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Hero Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <Badge className="bg-gradient-to-r from-purple-600 to-pink-600 text-white mb-6 text-lg py-2 px-6">
            🚀 30 English Proficiency Exams
          </Badge>
          <h1 className="text-6xl md:text-7xl font-extrabold text-gray-900 mb-6 leading-tight">
            Master <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              Every English Test
            </span>
          </h1>
          <p className="text-2xl text-gray-600 max-w-4xl mx-auto mb-10">
            From TOEFL to Cambridge, IELTS to OET – Complete preparation for all 30 major English proficiency exams with AI-powered practice
          </p>
          
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            <Button size="lg" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-6 text-lg">
              <GraduationCap className="mr-2" />
              Start Free Trial
            </Button>
            <Button size="lg" variant="outline" className="px-8 py-6 text-lg">
              <Building className="mr-2" />
              For Institutions
            </Button>
          </div>
          
          {/* Quick Stats */}
          <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="bg-white/50 backdrop-blur rounded-2xl p-4">
              <div className="text-3xl font-bold text-purple-600">30</div>
              <div className="text-sm text-gray-600">Exam Types</div>
            </div>
            <div className="bg-white/50 backdrop-blur rounded-2xl p-4">
              <div className="text-3xl font-bold text-pink-600">11</div>
              <div className="text-sm text-gray-600">Exam Families</div>
            </div>
            <div className="bg-white/50 backdrop-blur rounded-2xl p-4">
              <div className="text-3xl font-bold text-blue-600">4</div>
              <div className="text-sm text-gray-600">Core Skills</div>
            </div>
            <div className="bg-white/50 backdrop-blur rounded-2xl p-4">
              <div className="text-3xl font-bold text-green-600">AI</div>
              <div className="text-sm text-gray-600">Powered</div>
            </div>
          </div>
        </div>
      </section>

      {/* All Exams Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white mb-4">
              Complete Coverage
            </Badge>
            <h2 className="text-5xl font-extrabold text-gray-900 mb-6">
              All 30 English Proficiency Exams
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Every major English test, organized by family. Choose your exam and start preparing with AI-powered mock tests.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {examFamilies.map((family) => (
              <ExamFamilyCard key={family.id} family={family} />
            ))}
          </div>

          {/* Summary Stats */}
          <div className="mt-16 bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-center text-gray-900 mb-6">
              📊 Exam Type Breakdown
            </h3>
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-4xl font-bold text-purple-600 mb-2">17</div>
                <div className="text-gray-700 font-medium">Tier 1 - Core Exams</div>
                <div className="text-sm text-gray-600">TOEFL, IELTS, PTE, OET</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-pink-600 mb-2">10</div>
                <div className="text-gray-700 font-medium">Tier 2 - Popular</div>
                <div className="text-sm text-gray-600">Cambridge, Linguaskill, TOEIC</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">3</div>
                <div className="text-gray-700 font-medium">Tier 3 - Specialized</div>
                <div className="text-sm text-gray-600">Trinity, Oxford, APTIS</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4 Skills Section */}
      <section className="py-20 px-6 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="bg-green-600 text-white mb-4">
              Complete Training
            </Badge>
            <h2 className="text-5xl font-extrabold text-gray-900 mb-6">
              All 4 Skills, AI-Powered Evaluation
            </h2>
            <p className="text-xl text-gray-600">
              Every exam includes comprehensive practice for all language skills
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <Card className="card-duo text-center p-8">
              <div className="w-20 h-20 bg-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Reading</h3>
              <p className="text-gray-600">AI comprehension analysis</p>
            </Card>
            
            <Card className="card-duo text-center p-8">
              <div className="w-20 h-20 bg-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Headphones className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Listening</h3>
              <p className="text-gray-600">Real exam audio conditions</p>
            </Card>
            
            <Card className="card-duo text-center p-8">
              <div className="w-20 h-20 bg-red-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Mic className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Speaking</h3>
              <p className="text-gray-600">AI avatar conversation</p>
            </Card>
            
            <Card className="card-duo text-center p-8">
              <div className="w-20 h-20 bg-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <PenTool className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Writing</h3>
              <p className="text-gray-600">Instant AI feedback</p>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-12 text-white">
            <h2 className="text-4xl font-extrabold mb-4">
              Ready to Master Your English Exam?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of students preparing with AI-powered practice
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Button size="lg" className="bg-white text-purple-600 hover:bg-gray-100 px-8 py-6 text-lg">
                Start Free Trial
              </Button>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 px-8 py-6 text-lg">
                Contact Sales
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
