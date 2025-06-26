"""
이력서 분석 및 키워드 추출 모듈
Resume analysis and keyword extraction module
"""

import os
import json
import re
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI

class ResumeAnalyzer:
    def __init__(self):
        self.openai_client = None
        if os.environ.get("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """PDF 파일에서 텍스트 추출"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"PDF 텍스트 추출 오류: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """DOCX 파일에서 텍스트 추출"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"DOCX 텍스트 추출 오류: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """파일 확장자에 따라 텍스트 추출"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            except:
                with open(file_path, 'r', encoding='cp949') as file:
                    return file.read()
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {file_extension}")
    
    def extract_keywords_with_ai(self, text: str) -> List[str]:
        """OpenAI를 사용하여 이력서에서 취업 키워드 추출"""
        if not self.openai_client:
            return self.extract_keywords_fallback(text)
        
        try:
            prompt = f"""
다음 이력서 내용을 분석하여 사람인(saramin.co.kr) 구직 사이트에서 검색할 때 효과적인 키워드 10개를 추출해주세요.

분석할 이력서 내용:
{text}

추출 기준:
1. 전공/학과 관련 키워드
2. 경력/경험 분야 키워드  
3. 기술/스킬 키워드
4. 산업/업종 키워드
5. 직무/포지션 키워드

한국어로 된 키워드만 추출하고, 사람인에서 실제로 검색이 잘 되는 용어를 우선적으로 선택해주세요.
JSON 형식으로 응답해주세요: {{"keywords": ["키워드1", "키워드2", ...]}}
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "당신은 한국의 취업 전문가입니다. 이력서를 분석하여 구직에 효과적인 키워드를 추출하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("keywords", [])[:10]  # 최대 10개
            
        except Exception as e:
            print(f"AI 키워드 추출 오류: {e}")
            return self.extract_keywords_fallback(text)
    
    def extract_keywords_fallback(self, text: str) -> List[str]:
        """AI 사용 불가시 기본 키워드 추출"""
        # 기술 관련 키워드
        tech_keywords = [
            "python", "java", "javascript", "react", "node", "sql", "데이터분석", 
            "머신러닝", "AI", "인공지능", "웹개발", "앱개발", "프로그래밍"
        ]
        
        # 업종/분야 키워드
        industry_keywords = [
            "바이오", "제약", "의료", "IT", "금융", "제조", "화학", "건설", 
            "마케팅", "영업", "기획", "디자인", "연구개발", "R&D"
        ]
        
        # 직무 키워드
        job_keywords = [
            "개발자", "엔지니어", "매니저", "분석가", "컨설턴트", "디자이너",
            "연구원", "기술영업", "프로젝트매니저", "PM", "QA", "QC"
        ]
        
        all_keywords = tech_keywords + industry_keywords + job_keywords
        found_keywords = []
        
        text_lower = text.lower()
        for keyword in all_keywords:
            if keyword.lower() in text_lower and keyword not in found_keywords:
                found_keywords.append(keyword)
        
        # 기본 키워드가 부족하면 현재 설정된 키워드 사용
        if len(found_keywords) < 5:
            default_keywords = ["바이오", "제약", "머신비젼", "기술영업", "프로젝트 매니저", "BM"]
            for keyword in default_keywords:
                if keyword not in found_keywords:
                    found_keywords.append(keyword)
        
        return found_keywords[:10]
    
    def analyze_resume(self, file_path: str) -> Dict[str, Any]:
        """이력서 전체 분석"""
        try:
            # 텍스트 추출
            text = self.extract_text_from_file(file_path)
            
            if not text.strip():
                raise ValueError("이력서에서 텍스트를 추출할 수 없습니다.")
            
            # 키워드 추출
            keywords = self.extract_keywords_with_ai(text)
            
            return {
                "success": True,
                "keywords": keywords,
                "text_length": len(text),
                "message": f"{len(keywords)}개의 키워드가 추출되었습니다."
            }
            
        except Exception as e:
            return {
                "success": False,
                "keywords": [],
                "error": str(e),
                "message": f"이력서 분석 중 오류가 발생했습니다: {str(e)}"
            }