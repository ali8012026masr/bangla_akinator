"""
Idempotent Database Seed Script for Bangla Akinator.
Ensures verified Bengali personalities and questions are populated without duplicates.
Expanded dataset with 35 discriminative questions and 38 curated characters.
"""

import asyncio
from datetime import datetime, timezone
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import get_database, init_db_indexes, close_database_connection
from app.core.logging_config import logger


# 35 Discriminative Questions
QUESTIONS = [
    {
        "question_code": "q_is_real_person",
        "text_bn": "এই চরিত্রটি কি একজন বাস্তব মানুষ?",
        "text_en": "Is this character a real human being?",
        "answer_type": "boolean",
        "active": True,
        "order": 1,
    },
    {
        "question_code": "q_is_alive",
        "text_bn": "এই ব্যক্তি কি বর্তমানে জীবিত আছেন?",
        "text_en": "Is this person currently alive?",
        "answer_type": "boolean",
        "active": True,
        "order": 2,
    },
    {
        "question_code": "q_is_male",
        "text_bn": "এই ব্যক্তি কি পুরুষ?",
        "text_en": "Is this person male?",
        "answer_type": "boolean",
        "active": True,
        "order": 3,
    },
    {
        "question_code": "q_is_bangladeshi",
        "text_bn": "এই ব্যক্তি কি বাংলাদেশের নাগরিক বা বাংলাদেশি বংশোদ্ভূত?",
        "text_en": "Is this person a Bangladeshi citizen or of Bangladeshi origin?",
        "answer_type": "boolean",
        "active": True,
        "order": 4,
    },
    {
        "question_code": "q_is_sports",
        "text_bn": "তিনি কি খেলাধুলার জগতের সাথে সম্পর্কিত?",
        "text_en": "Is this person involved in sports?",
        "answer_type": "boolean",
        "active": True,
        "order": 5,
    },
    {
        "question_code": "q_is_cricketer",
        "text_bn": "তিনি কি একজন ক্রিকেটার?",
        "text_en": "Is this person a cricketer?",
        "answer_type": "boolean",
        "active": True,
        "order": 6,
    },
    {
        "question_code": "q_is_footballer",
        "text_bn": "তিনি কি ফুটবলের সাথে যুক্ত?",
        "text_en": "Is this person associated with football?",
        "answer_type": "boolean",
        "active": True,
        "order": 7,
    },
    {
        "question_code": "q_is_writer",
        "text_bn": "তিনি কি একজন লেখক বা কথাসাহিত্যিক?",
        "text_en": "Is this person an author or fiction writer?",
        "answer_type": "boolean",
        "active": True,
        "order": 8,
    },
    {
        "question_code": "q_is_poet",
        "text_bn": "তিনি কি মূলত কবি হিসেবে খ্যাত?",
        "text_en": "Is this person primarily renowned as a poet?",
        "answer_type": "boolean",
        "active": True,
        "order": 9,
    },
    {
        "question_code": "q_is_actor",
        "text_bn": "তিনি কি নাটক বা চলচ্চিত্রে অভিনয় করেছেন?",
        "text_en": "Has this person acted in television dramas or films?",
        "answer_type": "boolean",
        "active": True,
        "order": 10,
    },
    {
        "question_code": "q_is_tv",
        "text_bn": "তিনি কি নিয়মিত টেলিভিশনে উপস্থাপনা বা নাটকে কাজ করেছেন?",
        "text_en": "Has this person worked regularly in TV dramas or hosting?",
        "answer_type": "boolean",
        "active": True,
        "order": 11,
    },
    {
        "question_code": "q_is_film_director",
        "text_bn": "তিনি কি চলচ্চিত্র পরিচালনা করেছেন?",
        "text_en": "Has this person directed movies?",
        "answer_type": "boolean",
        "active": True,
        "order": 12,
    },
    {
        "question_code": "q_is_musician",
        "text_bn": "তিনি কি সংগীতশিল্পী বা গান করেন?",
        "text_en": "Is this person a musician or singer?",
        "answer_type": "boolean",
        "active": True,
        "order": 13,
    },
    {
        "question_code": "q_is_band",
        "text_bn": "তিনি কি কোনো ব্যান্ড সংগীত দলের সাথে যুক্ত ছিলেন?",
        "text_en": "Has this person been associated with a musical band?",
        "answer_type": "boolean",
        "active": True,
        "order": 14,
    },
    {
        "question_code": "q_is_politician",
        "text_bn": "তিনি কি সক্রিয় রাজনীতির সাথে যুক্ত বা সংসদ সদস্য ছিলেন?",
        "text_en": "Has this person been active in politics or an MP?",
        "answer_type": "boolean",
        "active": True,
        "order": 15,
    },
    {
        "question_code": "q_is_historical",
        "text_bn": "তিনি কি বাংলাদেশের মুক্তিযুদ্ধ বা ব্রিটিশ বিরোধী আন্দোলনের ঐতিহাসিক ব্যক্তিত্ব?",
        "text_en": "Is this person a historical figure of the Liberation War or anti-British movement?",
        "answer_type": "boolean",
        "active": True,
        "order": 16,
    },
    {
        "question_code": "q_is_scientist",
        "text_bn": "তিনি কি বিজ্ঞান বা গবেষণার সাথে জড়িত?",
        "text_en": "Is this person a scientist or academic researcher?",
        "answer_type": "boolean",
        "active": True,
        "order": 17,
    },
    {
        "question_code": "q_is_military",
        "text_bn": "তিনি কি সামরিক বাহিনীর সদস্য ছিলেন?",
        "text_en": "Was this person a member of the military forces?",
        "answer_type": "boolean",
        "active": True,
        "order": 18,
    },
    {
        "question_code": "q_is_nobel",
        "text_bn": "তিনি কি নোবেল পুরস্কার লাভ করেছেন?",
        "text_en": "Has this person received a Nobel Prize?",
        "answer_type": "boolean",
        "active": True,
        "order": 19,
    },
    {
        "question_code": "q_is_internet_celeb",
        "text_bn": "তিনি কি মূলত ইউটিউব বা সোশ্যাল মিডিয়ার মাধ্যমে জনপ্রিয়তা পেয়েছেন?",
        "text_en": "Did this person gain prominence primarily through YouTube or social media?",
        "answer_type": "boolean",
        "active": True,
        "order": 20,
    },
    {
        "question_code": "q_is_fictional_detective",
        "text_bn": "এই চরিত্রটি কি একজন কাল্পনিক গোয়েন্দা বা রহস্য সমাধানকারী?",
        "text_en": "Is this character a fictional detective or mystery solver?",
        "answer_type": "boolean",
        "active": True,
        "order": 21,
    },
    {
        "question_code": "q_wears_yellow_punjabi",
        "text_bn": "এই চরিত্র কি পকেট ছাড়া হলুদ পাঞ্জাবি পরার জন্য পরিচিত?",
        "text_en": "Is this character famous for wearing a yellow Punjabi without pockets?",
        "answer_type": "boolean",
        "active": True,
        "order": 22,
    },
    {
        "question_code": "q_is_prime_minister_or_president",
        "text_bn": "তিনি কি কখনও বাংলাদেশের সরকার প্রধান (প্রধানমন্ত্রী/রাষ্ট্রপতি) ছিলেন?",
        "text_en": "Was this person ever the head of state or government (President/PM) of Bangladesh?",
        "answer_type": "boolean",
        "active": True,
        "order": 23,
    },
    {
        "question_code": "q_is_fast_bowler",
        "text_bn": "তিনি কি একজন ফাস্ট বোলার বা পেসার?",
        "text_en": "Is this cricketer a fast bowler or pacer?",
        "answer_type": "boolean",
        "active": True,
        "order": 24,
    },
    {
        "question_code": "q_is_batsman_or_opener",
        "text_bn": "তিনি কি মূলত উদ্বোধনী ব্যাটসম্যান বা মারকুটে ব্যাটার?",
        "text_en": "Is this person primarily known as an opening batsman?",
        "answer_type": "boolean",
        "active": True,
        "order": 25,
    },
    {
        "question_code": "q_is_rock_musician",
        "text_bn": "তিনি কি বাংলা রক বা মেটাল ঘরানার সংগীতের সাথে জড়িত?",
        "text_en": "Is this person involved in Bangla rock music?",
        "answer_type": "boolean",
        "active": True,
        "order": 26,
    },
    {
        "question_code": "q_is_folk_or_mystic_singer",
        "text_bn": "তিনি কি বাউল, সুফি বা লোকসংগীতের সাধক/শিল্পী ছিলেন?",
        "text_en": "Is this person a mystic, Baul, or folk music philosopher/artist?",
        "answer_type": "boolean",
        "active": True,
        "order": 27,
    },
    {
        "question_code": "q_is_national_poet",
        "text_bn": "তিনি কি বাংলাদেশের জাতীয় কবি?",
        "text_en": "Is this person the National Poet of Bangladesh?",
        "answer_type": "boolean",
        "active": True,
        "order": 28,
    },
    {
        "question_code": "q_won_oscar",
        "text_bn": "তিনি কি অস্কার (একাডেমি পুরস্কার) লাভ করেছেন?",
        "text_en": "Has this person won an Academy Award (Oscar)?",
        "answer_type": "boolean",
        "active": True,
        "order": 29,
    },
    {
        "question_code": "q_is_female_pioneer",
        "text_bn": "তিনি কি বাঙালি নারী জাগরণ ও নারী শিক্ষার অগ্রদূত ছিলেন?",
        "text_en": "Was this person a pioneer in Bengali women's education and awakening?",
        "answer_type": "boolean",
        "active": True,
        "order": 30,
    },
    {
        "question_code": "q_is_chess_player",
        "text_bn": "তিনি কি দাবা খেলার সাথে যুক্ত বা আন্তর্জাতিক গ্র্যান্ডমাস্টার?",
        "text_en": "Is this person associated with chess or an International Grandmaster?",
        "answer_type": "boolean",
        "active": True,
        "order": 31,
    },
    {
        "question_code": "q_is_comedian_or_satirist",
        "text_bn": "তিনি কি কমেডি বা ব্যঙ্গাত্মক চরিত্রে অভিনয়ের জন্য বিশেষভাবে সুপরিচিত?",
        "text_en": "Is this person uniquely renowned for comedy or satirical acting?",
        "answer_type": "boolean",
        "active": True,
        "order": 32,
    },
    {
        "question_code": "q_is_physicist_or_botanist",
        "text_bn": "তিনি কি পদার্থবিজ্ঞান বা উদ্ভিদবিদ্যার গবেষণায় আন্তর্জাতিক খ্যাতিমান?",
        "text_en": "Is this person internationally renowned in physics or plant research?",
        "answer_type": "boolean",
        "active": True,
        "order": 33,
    },
    {
        "question_code": "q_is_economist_or_banker",
        "text_bn": "তিনি কি অর্থনীতি বা গ্রামীণ ক্ষুদ্রঋণ ব্যাংকিংয়ের পথিকৃৎ?",
        "text_en": "Is this person a pioneer in economics or microcredit banking?",
        "answer_type": "boolean",
        "active": True,
        "order": 34,
    },
    {
        "question_code": "q_is_edtech_founder",
        "text_bn": "তিনি কি কোনো বৃহৎ অনলাইন শিক্ষা প্ল্যাটফর্মের প্রতিষ্ঠাতা?",
        "text_en": "Is this person the founder of a major online educational platform?",
        "answer_type": "boolean",
        "active": True,
        "order": 35,
    },
]


def make_fact(val: bool):
    return {"value": val, "confidence": 1.0, "source": "editor_verified"}


# Helper to generate full profile given True questions and default rest to False
ALL_Q_CODES = [q["question_code"] for q in QUESTIONS]


def full_profile(true_codes: list) -> dict:
    t_set = set(true_codes)
    return {code: make_fact(code in t_set) for code in ALL_Q_CODES}


CHARACTERS = [
    # 1. সাকিব আল হাসান
    {
        "name_bn": "সাকিব আল হাসান",
        "name_en": "Shakib Al Hasan",
        "normalized_name": "সাকিব আল হাসান",
        "aliases_bn": ["সাকিব"],
        "aliases_en": ["Shakib", "Shakib Al Hasan"],
        "categories": ["ক্রিকেটার", "ক্রীড়াবিদ", "রাজনীতিবিদ"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_sports", "q_is_cricketer", "q_is_politician"
        ])
    },
    # 2. মাশরাফি বিন মুর্তজা
    {
        "name_bn": "মাশরাফি বিন মুর্তজা",
        "name_en": "Mashrafe Bin Mortaza",
        "normalized_name": "মাশরাফি বিন মুর্তজা",
        "aliases_bn": ["মাশরাফি", "নড়াইল এক্সপ্রেস"],
        "aliases_en": ["Mashrafe", "Narail Express"],
        "categories": ["ক্রিকেটার", "ক্রীড়াবিদ", "রাজনীতিবিদ"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_sports", "q_is_cricketer", "q_is_politician", "q_is_fast_bowler"
        ])
    },
    # 3. তামিম ইকবাল
    {
        "name_bn": "তামিম ইকবাল",
        "name_en": "Tamim Iqbal",
        "normalized_name": "তামিম ইকবাল",
        "aliases_bn": ["তামিম"],
        "aliases_en": ["Tamim", "Tamim Iqbal"],
        "categories": ["ক্রিকেটার", "ক্রীড়াবিদ"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_sports", "q_is_cricketer", "q_is_batsman_or_opener"
        ])
    },
    # 4. মুস্তাফিজুর রহমান
    {
        "name_bn": "মুস্তাফিজুর রহমান",
        "name_en": "Mustafizur Rahman",
        "normalized_name": "মুস্তাফিজুর রহমান",
        "aliases_bn": ["মুস্তাফিজ", "দ্য কাটার মাস্টার"],
        "aliases_en": ["Mustafiz", "Cutter Master"],
        "categories": ["ক্রিকেটার", "ক্রীড়াবিদ"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_sports", "q_is_cricketer", "q_is_fast_bowler"
        ])
    },
    # 5. জামাল ভূঁইয়া
    {
        "name_bn": "জামাল ভূঁইয়া",
        "name_en": "Jamal Bhuyan",
        "normalized_name": "জামাল ভূঁইয়া",
        "aliases_bn": ["জামাল ভূইয়া", "ক্যাপ্টেন জামাল"],
        "aliases_en": ["Jamal Bhuyan"],
        "categories": ["ফুটবলার", "ক্রীড়াবিদ"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_sports", "q_is_footballer"
        ])
    },
    # 6. নিয়াজ মোর্শেদ
    {
        "name_bn": "নিয়াজ মোর্শেদ",
        "name_en": "Niaz Murshed",
        "normalized_name": "নিয়াজ মোর্শেদ",
        "aliases_bn": ["গ্র্যান্ডমাস্টার নিয়াজ মোর্শেদ"],
        "aliases_en": ["Niaz Murshed"],
        "categories": ["দাবারু", "ক্রীড়াবিদ"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_sports", "q_is_chess_player"
        ])
    },
    # 7. কাজী নজরুল ইসলাম
    {
        "name_bn": "কাজী নজরুল ইসলাম",
        "name_en": "Kazi Nazrul Islam",
        "normalized_name": "কাজী নজরুল ইসলাম",
        "aliases_bn": ["নজরুল", "বিদ্রোহী কবি"],
        "aliases_en": ["Nazrul", "Rebel Poet"],
        "categories": ["কবি", "লেখক", "সুরকার", "জাতীয় কবি"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_writer",
            "q_is_poet", "q_is_musician", "q_is_historical", "q_is_national_poet"
        ])
    },
    # 8. রবীন্দ্রনাথ ঠাকুর
    {
        "name_bn": "রবীন্দ্রনাথ ঠাকুর",
        "name_en": "Rabindranath Tagore",
        "normalized_name": "রবীন্দ্রনাথ ঠাকুর",
        "aliases_bn": ["বিশ্বকবি", "রবি ঠাকুর"],
        "aliases_en": ["Tagore", "Rabi Thakur"],
        "categories": ["কবি", "লেখক", "সুরকার", "নোবেল বিজয়ী"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_writer", "q_is_poet",
            "q_is_musician", "q_is_historical", "q_is_nobel"
        ])
    },
    # 9. জসীম উদ্দীন
    {
        "name_bn": "জসীম উদ্দীন",
        "name_en": "Jasimuddin",
        "normalized_name": "জসীম উদ্দীন",
        "aliases_bn": ["পল্লীকবি", "জসিমউদ্দিন"],
        "aliases_en": ["Jasimuddin", "Polli Kobi"],
        "categories": ["কবি", "লেখক"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_writer",
            "q_is_poet", "q_is_historical"
        ])
    },
    # 10. জীবনানন্দ দাশ
    {
        "name_bn": "জীবনানন্দ দাশ",
        "name_en": "Jibanananda Das",
        "normalized_name": "জীবনানন্দ দাশ",
        "aliases_bn": ["রুপসী বাংলার কবি", "বনলতা সেনের কবি"],
        "aliases_en": ["Jibanananda Das"],
        "categories": ["কবি", "লেখক"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_writer", "q_is_poet",
            "q_is_historical"
        ])
    },
    # 11. হুমায়ূন আহমেদ
    {
        "name_bn": "হুমায়ূন আহমেদ",
        "name_en": "Humayun Ahmed",
        "normalized_name": "হুমায়ূন আহমেদ",
        "aliases_bn": ["হুমায়ূন আহমেদ"],
        "aliases_en": ["Humayun Ahmed"],
        "categories": ["লেখক", "চলচ্চিত্র পরিচালক", "নাট্যকার"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_writer",
            "q_is_tv", "q_is_film_director"
        ])
    },
    # 12. বেগম রোকেয়া
    {
        "name_bn": "বেগম রোকেয়া",
        "name_en": "Begum Rokeya",
        "normalized_name": "বেগম রোকেয়া",
        "aliases_bn": ["রোকেয়া সাখাওয়াত হোসেন"],
        "aliases_en": ["Rokeya Sakhawat Hossain", "Begum Rokeya"],
        "categories": ["লেখক", "সমাজ সংস্কারক", "নারী জাগরণের অগ্রদূত"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_bangladeshi", "q_is_writer",
            "q_is_historical", "q_is_female_pioneer"
        ])
    },
    # 13. সত্যজিৎ রায়
    {
        "name_bn": "সত্যজিৎ রায়",
        "name_en": "Satyajit Ray",
        "normalized_name": "সত্যজিৎ রায়",
        "aliases_bn": ["মানিক দা"],
        "aliases_en": ["Satyajit Ray"],
        "categories": ["চলচ্চিত্র পরিচালক", "লেখক", "অস্কার বিজয়ী"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_writer", "q_is_film_director",
            "q_is_musician", "q_is_historical", "q_won_oscar"
        ])
    },
    # 14. চঞ্চল চৌধুরী
    {
        "name_bn": "চঞ্চল চৌধুরী",
        "name_en": "Chanchal Chowdhury",
        "normalized_name": "চঞ্চল চৌধুরী",
        "aliases_bn": ["চঞ্চল"],
        "aliases_en": ["Chanchal Chowdhury"],
        "categories": ["অভিনেতা", "মডেল"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_actor", "q_is_tv", "q_is_musician"
        ])
    },
    # 15. মোশাররফ করিম
    {
        "name_bn": "মোশাররফ করিম",
        "name_en": "Mosharraf Karim",
        "normalized_name": "মোশাররফ করিম",
        "aliases_bn": ["মোশারফ করিম"],
        "aliases_en": ["Mosharraf Karim"],
        "categories": ["অভিনেতা"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_actor", "q_is_tv", "q_is_comedian_or_satirist"
        ])
    },
    # 16. হুমায়ুন ফরিদী
    {
        "name_bn": "হুমায়ুন ফরিদী",
        "name_en": "Humayun Faridi",
        "normalized_name": "হুমায়ুন ফরিদী",
        "aliases_bn": ["ফরিদী ভাই"],
        "aliases_en": ["Humayun Faridi"],
        "categories": ["অভিনেতা"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_actor",
            "q_is_tv", "q_is_historical", "q_is_comedian_or_satirist"
        ])
    },
    # 17. সালমান শাহ
    {
        "name_bn": "সালমান শাহ",
        "name_en": "Salman Shah",
        "normalized_name": "সালমান শাহ",
        "aliases_bn": ["ইমন"],
        "aliases_en": ["Salman Shah", "Emon"],
        "categories": ["চলচ্চিত্র অভিনেতা"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_actor"
        ])
    },
    # 18. আবদুর রাজ্জাক (নায়করাজ রাজ্জাক)
    {
        "name_bn": "আবদুর রাজ্জাক",
        "name_en": "Abdur Razzak",
        "normalized_name": "আবদুর রাজ্জাক",
        "aliases_bn": ["নায়করাজ রাজ্জাক", "রাজ্জাক"],
        "aliases_en": ["Nayak Raj Razzak", "Abdur Razzak"],
        "categories": ["অভিনেতা", "চলচ্চিত্র পরিচালক"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_actor",
            "q_is_film_director", "q_is_historical"
        ])
    },
    # 19. জয়া আহসান
    {
        "name_bn": "জয়া আহসান",
        "name_en": "Jaya Ahsan",
        "normalized_name": "জয়া আহসান",
        "aliases_bn": ["জয়া"],
        "aliases_en": ["Jaya Ahsan"],
        "categories": ["অভিনেত্রী", "মডেল"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_bangladeshi",
            "q_is_actor", "q_is_tv"
        ])
    },
    # 20. জেমস (মাহফুজ আনাম জেমস)
    {
        "name_bn": "জেমস",
        "name_en": "James",
        "normalized_name": "জেমস",
        "aliases_bn": ["নগর বাউল", "মাহফুজ আনাম জেমস", "গুরু"],
        "aliases_en": ["Nagar Baul James", "Guru James"],
        "categories": ["সংগীতশিল্পী", "ব্যান্ড তারকা"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_musician", "q_is_band", "q_is_rock_musician"
        ])
    },
    # 21. আইয়ুব বাচ্চু
    {
        "name_bn": "আইয়ুব বাচ্চু",
        "name_en": "Ayub Bachchu",
        "normalized_name": "আইয়ুব বাচ্চু",
        "aliases_bn": ["এবি", "এলআরবি বাচ্চু"],
        "aliases_en": ["Ayub Bachchu", "AB", "LRB"],
        "categories": ["সংগীতশিল্পী", "গিটারিস্ট", "ব্যান্ড তারকা"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi",
            "q_is_musician", "q_is_band", "q_is_rock_musician"
        ])
    },
    # 22. তাহসান খান
    {
        "name_bn": "তাহসান খান",
        "name_en": "Tahsan Khan",
        "normalized_name": "তাহসান খান",
        "aliases_bn": ["তাহসান রহমান খান"],
        "aliases_en": ["Tahsan", "Tahsan Rahman Khan"],
        "categories": ["সংগীতশিল্পী", "অভিনেতা"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_actor", "q_is_tv", "q_is_musician", "q_is_band"
        ])
    },
    # 23. রুনা লায়লা
    {
        "name_bn": "রুনা লায়লা",
        "name_en": "Runa Laila",
        "normalized_name": "রুনা লায়লা",
        "aliases_bn": ["রুনা"],
        "aliases_en": ["Runa Laila"],
        "categories": ["সংগীতশিল্পী", "প্লেব্যাক গায়িকা"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_bangladeshi",
            "q_is_musician", "q_is_tv"
        ])
    },
    # 24. ফকির লালন শাহ
    {
        "name_bn": "ফকির লালন শাহ",
        "name_en": "Fakir Lalon Shah",
        "normalized_name": "ফকির লালন শাহ",
        "aliases_bn": ["লালন সাঁই", "মহাত্মা লালন"],
        "aliases_en": ["Lalon Shah", "Lalon Shai"],
        "categories": ["বাউল সাধক", "গীতিকার", "দার্শনিক"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_poet",
            "q_is_musician", "q_is_historical", "q_is_folk_or_mystic_singer"
        ])
    },
    # 25. বঙ্গবন্ধু শেখ মুজিবুর রহমান
    {
        "name_bn": "বঙ্গবন্ধু শেখ মুজিবুর রহমান",
        "name_en": "Bangabandhu Sheikh Mujibur Rahman",
        "normalized_name": "বঙ্গবন্ধু শেখ মুজিবুর রহমান",
        "aliases_bn": ["বঙ্গবন্ধু", "শেখ মুজিব", "জাতির পিতা"],
        "aliases_en": ["Sheikh Mujib", "Father of the Nation"],
        "categories": ["রাজনীতিবিদ", "জাতির পিতা", "রাষ্ট্রপ্রধান"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_politician",
            "q_is_historical", "q_is_prime_minister_or_president"
        ])
    },
    # 26. জিয়াউর রহমান
    {
        "name_bn": "জিয়াউর রহমান",
        "name_en": "Ziaur Rahman",
        "normalized_name": "জিয়াউর রহমান",
        "aliases_bn": ["জিয়া", "বীর উত্তম জিয়া"],
        "aliases_en": ["Ziaur Rahman", "Zia"],
        "categories": ["রাষ্ট্রপতি", "সামরিক কর্মকর্তা", "রাজনীতিবিদ"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_politician",
            "q_is_historical", "q_is_military", "q_is_prime_minister_or_president"
        ])
    },
    # 27. তাজউদ্দীন আহমদ
    {
        "name_bn": "তাজউদ্দীন আহমদ",
        "name_en": "Tajuddin Ahmad",
        "normalized_name": "তাজউদ্দীন আহমদ",
        "aliases_bn": ["তাজউদ্দিন আহমেদ"],
        "aliases_en": ["Tajuddin Ahmad"],
        "categories": ["রাজনীতিবিদ", "প্রথম প্রধানমন্ত্রী", "জাতীয় নেতা"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_writer",
            "q_is_politician", "q_is_historical", "q_is_prime_minister_or_president"
        ])
    },
    # 28. মওলানা আবদুল হামিদ খান ভাসানী
    {
        "name_bn": "মওলানা আবদুল হামিদ খান ভাসানী",
        "name_en": "Maulana Abdul Hamid Khan Bhashani",
        "normalized_name": "মওলানা আবদুল হামিদ খান ভাসানী",
        "aliases_bn": ["মওলানা ভাসানী", "মজলুম জননেতা"],
        "aliases_en": ["Maulana Bhashani", "Majlum Jananeta"],
        "categories": ["রাজনীতিবিদ", "জননেতা"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_politician",
            "q_is_historical"
        ])
    },
    # 29. ড. মুহাম্মদ ইউনূস
    {
        "name_bn": "ড. মুহাম্মদ ইউনূস",
        "name_en": "Dr. Muhammad Yunus",
        "normalized_name": "ড. মুহাম্মদ ইউনূস",
        "aliases_bn": ["মুহাম্মদ ইউনূস"],
        "aliases_en": ["Muhammad Yunus"],
        "categories": ["অর্থনীতিবিদ", "নোবেল বিজয়ী", "শিক্ষাবিদ"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_writer", "q_is_nobel", "q_is_economist_or_banker"
        ])
    },
    # 30. স্যার জগদীশ চন্দ্র বসু
    {
        "name_bn": "স্যার জগদীশ চন্দ্র বসু",
        "name_en": "Sir Jagadish Chandra Bose",
        "normalized_name": "স্যার জগদীশ চন্দ্র বসু",
        "aliases_bn": ["জগদীশ চন্দ্র বসু", "জেসি বোস"],
        "aliases_en": ["J. C. Bose", "Jagadish Chandra Bose"],
        "categories": ["বিজ্ঞানী", "উদ্ভিদবিদ", "পদার্থবিজ্ঞানী"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi", "q_is_writer",
            "q_is_historical", "q_is_scientist", "q_is_physicist_or_botanist"
        ])
    },
    # 31. অধ্যাপক জামাল নজরুল ইসলাম
    {
        "name_bn": "অধ্যাপক জামাল নজরুল ইসলাম",
        "name_en": "Jamal Nazrul Islam",
        "normalized_name": "অধ্যাপক জামাল নজরুল ইসলাম",
        "aliases_bn": ["জামাল নজরুল ইসলাম"],
        "aliases_en": ["Jamal Nazrul Islam", "J. N. Islam"],
        "categories": ["বিজ্ঞানী", "পদার্থবিজ্ঞানী", "গণিতবিদ"],
        "is_real_person": True,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_male", "q_is_bangladeshi",
            "q_is_scientist", "q_is_physicist_or_botanist"
        ])
    },
    # 32. আয়মান সাদিক
    {
        "name_bn": "আয়মান সাদিক",
        "name_en": "Ayman Sadiq",
        "normalized_name": "আয়মান সাদিক",
        "aliases_bn": ["আয়মান"],
        "aliases_en": ["Ayman Sadiq"],
        "categories": ["শিক্ষাবিদ", "ইউটিউবার", "উদ্যোক্তা"],
        "is_real_person": True,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_real_person", "q_is_alive", "q_is_male", "q_is_bangladeshi",
            "q_is_writer", "q_is_internet_celeb", "q_is_edtech_founder"
        ])
    },
    # 33. হিমু
    {
        "name_bn": "হিমু",
        "name_en": "Himu",
        "normalized_name": "হিমু",
        "aliases_bn": ["হিমালয়"],
        "aliases_en": ["Himu", "Himaloy"],
        "categories": ["কাল্পনিক চরিত্র", "সাহিত্য"],
        "is_real_person": False,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_alive", "q_is_male", "q_is_bangladeshi", "q_wears_yellow_punjabi"
        ])
    },
    # 34. মিসির আলি
    {
        "name_bn": "মিসির আলি",
        "name_en": "Misir Ali",
        "normalized_name": "মিসির আলি",
        "aliases_bn": ["মিসির আলী"],
        "aliases_en": ["Misir Ali"],
        "categories": ["কাল্পনিক চরিত্র", "গোয়েন্দা", "সাহিত্য"],
        "is_real_person": False,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_alive", "q_is_male", "q_is_bangladeshi", "q_is_scientist",
            "q_is_fictional_detective"
        ])
    },
    # 35. ফেলুদা
    {
        "name_bn": "ফেলুদা",
        "name_en": "Feluda",
        "normalized_name": "ফেলুদা",
        "aliases_bn": ["প্রদোষ চন্দ্র মিত্র", "প্রদোষ সি মিত্র"],
        "aliases_en": ["Feluda", "Prodosh Chandra Mitter"],
        "categories": ["কাল্পনিক চরিত্র", "গোয়েন্দা"],
        "is_real_person": False,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_alive", "q_is_male", "q_is_fictional_detective"
        ])
    },
    # 36. ব্যোমকেশ বক্সী
    {
        "name_bn": "ব্যোমকেশ বক্সী",
        "name_en": "Byomkesh Bakshi",
        "normalized_name": "ব্যোমকেশ বক্সী",
        "aliases_bn": ["সত্যান্বেষী"],
        "aliases_en": ["Byomkesh", "Satyanweshi"],
        "categories": ["কাল্পনিক চরিত্র", "গোয়েন্দা"],
        "is_real_person": False,
        "is_alive": False,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_male", "q_is_historical", "q_is_fictional_detective"
        ])
    },
    # 37. মাসুদ রানা
    {
        "name_bn": "মাসুদ রানা",
        "name_en": "Masud Rana",
        "normalized_name": "মাসুদ রানা",
        "aliases_bn": ["রানা", "এমআর-নাইন"],
        "aliases_en": ["Masud Rana", "MR-9"],
        "categories": ["কাল্পনিক চরিত্র", "গুপ্তচর", "সাহিত্য"],
        "is_real_person": False,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_alive", "q_is_male", "q_is_bangladeshi", "q_is_military",
            "q_is_fictional_detective"
        ])
    },
    # 38. প্রফেসর শঙ্কু
    {
        "name_bn": "প্রফেসর শঙ্কু",
        "name_en": "Professor Shonku",
        "normalized_name": "প্রফেসর শঙ্কু",
        "aliases_bn": ["ত্রিলোকেশ্বর শঙ্কু", "প্রফেসর ত্রিলোকেশ্বর শঙ্কু"],
        "aliases_en": ["Professor Shonku", "Trilokeshwar Shonku"],
        "categories": ["কাল্পনিক চরিত্র", "বিজ্ঞানী", "সাহিত্য"],
        "is_real_person": False,
        "is_alive": True,
        "image_url": None,
        "status": "published",
        "answer_profile": full_profile([
            "q_is_alive", "q_is_male", "q_is_scientist"
        ])
    },
]


async def seed_data():
    """Seed questions and characters into MongoDB."""
    db = get_database()
    await init_db_indexes()

    now = datetime.now(timezone.utc)

    # Step 1: Upsert questions
    for q in QUESTIONS:
        await db.questions.update_one(
            {"question_code": q["question_code"]},
            {
                "$set": {
                    "text_bn": q["text_bn"],
                    "text_en": q["text_en"],
                    "answer_type": q["answer_type"],
                    "active": q["active"],
                    "order": q["order"],
                    "updated_at": now
                },
                "$setOnInsert": {
                    "created_at": now
                }
            },
            upsert=True
        )
    logger.info(f"Seeded {len(QUESTIONS)} questions (idempotent upsert).")

    # Step 2: Upsert characters
    for c in CHARACTERS:
        await db.characters.update_one(
            {"normalized_name": c["normalized_name"]},
            {
                "$set": {
                    "name_bn": c["name_bn"],
                    "name_en": c["name_en"],
                    "aliases_bn": c["aliases_bn"],
                    "aliases_en": c["aliases_en"],
                    "categories": c["categories"],
                    "is_real_person": c["is_real_person"],
                    "is_alive": c["is_alive"],
                    "image_url": c["image_url"],
                    "status": c["status"],
                    "answer_profile": c["answer_profile"],
                    "updated_at": now
                },
                "$setOnInsert": {
                    "created_at": now,
                    "times_played": 0,
                    "times_guessed_correctly": 0
                }
            },
            upsert=True
        )
    logger.info(f"Seeded {len(CHARACTERS)} characters (idempotent upsert).")

    total_q = await db.questions.count_documents({})
    total_c = await db.characters.count_documents({})
    logger.info(f"Database currently contains {total_q} questions and {total_c} characters.")


async def main():
    try:
        await seed_data()
    finally:
        await close_database_connection()


if __name__ == "__main__":
    asyncio.run(main())
