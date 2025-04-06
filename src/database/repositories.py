from sqlmodel import Session, select
from src.database.connection import engine
from src.database.models import En_Ptbr


class EnPtbrRepository:

    @staticmethod
    def get_all():
        data = {'id': [], 'en': [], 'ptbr': [], 'mod': []}
        with Session(engine) as session:
            statement = select(En_Ptbr)
            results = session.exec(statement).all()
        
        for result in results:
            data['id'].append(result.id)
            data['en'].append(result.en)
            data['ptbr'].append(result.ptbr)
            data['mod'].append(result.mod)
        return data

        

    @staticmethod
    def add_one(en, ptbr, mod):

        if ptbr is None or ptbr.strip() == '':
            return None
        
        if en is None or en.strip() == '':
            return None
        
        if mod is None or mod.strip() == '':
            return None


        data = En_Ptbr(en=en, ptbr=ptbr, mod=mod)
        with Session(engine) as session:
            session.add(data)
            session.commit()
            session.refresh(data)
            return data
        

    @staticmethod
    def add_many(data: dict[str, list]):

        required_keys = ['en', 'ptbr', 'mod']
        if not all([key in data.keys() for key in required_keys]):
            raise ValueError(f'Chave obrigatória não encontrada: {required_keys}')
        

        list_lengths = [len(data[key]) for key in required_keys if key in data]
        if len(set(list_lengths)) > 1:
            raise ValueError(f'Listas de tamanhos diferentes: {list_lengths}')


        models = []
        for i in range(list_lengths[0]):
            model = En_Ptbr(
                en=data['en'][i],
                ptbr=data['ptbr'][i],
                mod=data['mod'][i]
            )
            models.append(model)


        with Session(engine) as session:
            session.add_all(models)
            session.commit()
            return models

    
    @staticmethod
    def find_by_en(en: str):
        with Session(engine) as session:
            statement = select(En_Ptbr).where(En_Ptbr.en == en)
            result = session.exec(statement).first()
            
            if result:
                return {
                    'id': result.id,
                    'en': result.en,
                    'ptbr': result.ptbr,
                    'mod': result.mod
                }
            
            return None
        
