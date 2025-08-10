from django.core.management.base import BaseCommand
from meetups.models import Meetup
import random

class Command(BaseCommand):
    help = 'Add sample hashtags to existing meetups'

    def handle(self, *args, **options):
        # Define hashtag categories based on meetup types
        hashtag_sets = {
            'tech': ['#개발', '#프로그래밍', '#코딩', '#IT', '#테크', '#소프트웨어'],
            'business': ['#비즈니스', '#스타트업', '#창업', '#마케팅', '#경영', '#투자'],
            'networking': ['#네트워킹', '#모임', '#소통', '#교류', '#커뮤니티', '#만남'],
            'learning': ['#학습', '#교육', '#스터디', '#세미나', '#워크샵', '#강의'],
            'design': ['#디자인', '#UX', '#UI', '#크리에이티브', '#아트', '#그래픽'],
            'finance': ['#금융', '#투자', '#주식', '#재테크', '#경제', '#암호화폐'],
            'health': ['#건강', '#웰빙', '#운동', '#요가', '#명상', '#라이프스타일'],
            'food': ['#음식', '#요리', '#카페', '#맛집', '#푸드', '#베이킹'],
            'book': ['#독서', '#책', '#도서', '#문학', '#작가', '#북클럽'],
            'hobby': ['#취미', '#여가', '#문화', '#예술', '#음악', '#영화']
        }

        meetups = Meetup.objects.all()
        
        for meetup in meetups:
            if meetup.hashtags:  # Skip if already has hashtags
                continue
            
            # Analyze meetup name and description to assign relevant hashtags
            name_desc = (meetup.name + ' ' + (meetup.description or '')).lower()
            
            selected_hashtags = []
            
            # Technology-related keywords
            tech_keywords = ['개발', '프로그래밍', '코딩', 'it', '테크', '소프트웨어', 'ai', '머신러닝', 'python', 'javascript', '웹개발']
            if any(keyword in name_desc for keyword in tech_keywords):
                selected_hashtags.extend(random.sample(hashtag_sets['tech'], min(2, len(hashtag_sets['tech']))))
            
            # Business keywords
            business_keywords = ['비즈니스', '스타트업', '창업', '마케팅', '경영', '투자', '사업']
            if any(keyword in name_desc for keyword in business_keywords):
                selected_hashtags.extend(random.sample(hashtag_sets['business'], min(2, len(hashtag_sets['business']))))
            
            # Learning keywords
            learning_keywords = ['학습', '교육', '스터디', '세미나', '워크샵', '강의', '독서', '책']
            if any(keyword in name_desc for keyword in learning_keywords):
                if '독서' in name_desc or '책' in name_desc:
                    selected_hashtags.extend(random.sample(hashtag_sets['book'], min(2, len(hashtag_sets['book']))))
                else:
                    selected_hashtags.extend(random.sample(hashtag_sets['learning'], min(2, len(hashtag_sets['learning']))))
            
            # Design keywords
            design_keywords = ['디자인', 'ux', 'ui', '크리에이티브', '아트', '그래픽']
            if any(keyword in name_desc for keyword in design_keywords):
                selected_hashtags.extend(random.sample(hashtag_sets['design'], min(2, len(hashtag_sets['design']))))
            
            # Finance keywords
            finance_keywords = ['금융', '투자', '주식', '재테크', '경제', '비트코인', '암호화폐', '블록체인']
            if any(keyword in name_desc for keyword in finance_keywords):
                selected_hashtags.extend(random.sample(hashtag_sets['finance'], min(2, len(hashtag_sets['finance']))))
            
            # Food keywords
            food_keywords = ['음식', '요리', '카페', '맛집', '푸드', '베이킹', '커피']
            if any(keyword in name_desc for keyword in food_keywords):
                selected_hashtags.extend(random.sample(hashtag_sets['food'], min(2, len(hashtag_sets['food']))))
            
            # Health keywords
            health_keywords = ['건강', '웰빙', '운동', '요가', '명상', '라이프스타일']
            if any(keyword in name_desc for keyword in health_keywords):
                selected_hashtags.extend(random.sample(hashtag_sets['health'], min(2, len(hashtag_sets['health']))))
            
            # Always add networking tags
            selected_hashtags.extend(random.sample(hashtag_sets['networking'], min(1, len(hashtag_sets['networking']))))
            
            # If no specific category matched, add general hobby tags
            if len(selected_hashtags) <= 1:
                selected_hashtags.extend(random.sample(hashtag_sets['hobby'], min(2, len(hashtag_sets['hobby']))))
            
            # Remove duplicates and limit to 5 hashtags max
            selected_hashtags = list(set(selected_hashtags))[:5]
            
            # Save hashtags to meetup
            meetup.hashtags = ','.join(selected_hashtags)
            meetup.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Added hashtags to "{meetup.name}": {", ".join(selected_hashtags)}')
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully added hashtags to all meetups'))